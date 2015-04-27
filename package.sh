#!/bin/bash

# This script is to package the web2board package for Windows/Linux
# This script should run under Linux and Mac OS X, as well as Windows with Cygwin.

#############################
# CONFIGURATION
#############################

##Select the build target
BUILD_TARGET=${1:-none}
#BUILD_TARGET=win32
#BUILD_TARGET=debian

EXTRA_ARGS=${2}

##Which version name are we appending to the final archive
VERSION=`head -1 pkg/linux/debian/changelog | grep -o '\(([^\)]*\)' | tr -d '()' | head -1`
VEXT=${VEXT:=""}
TARGET_DIR=web2board-${VERSION}-${BUILD_TARGET}

##Which versions of external programs to use
WIN_PORTABLE_PY_VERSION=2.7.2.1 #TODO: 2.7.6.1


#############################
# Support functions
#############################
function checkTool
{
	if [ -z `which $1` ]; then
		echo "The $1 command must be somewhere in your \$PATH."
		echo "Fix your \$PATH or install it"
		exit 1
	fi
}

function downloadURL
{
	filename=`basename "$1"`
	echo "Checking for $filename"
	if [ ! -f "$filename" ]; then
		echo "Downloading $1"
		curl -L -O "$1"
		if [ $? != 0 ]; then
			echo "Failed to download $1"
			exit 1
		fi
	fi
}

function extract
{
	if [ $1 != ${1%%.exe} ] || [ $1 != ${1%%.zip} ] || [ $1 != ${1%%.msi} ]; then
		echo "Extracting $*"
		echo "7z x -y $*" >> log.txt
		7z x -y $* >> log.txt
		if [ $? != 0 ]; then
			echo "Failed to extract $*"
			exit 1
		fi
	elif [ $1 != ${1%%.tar.gz} ]; then
		echo "Extracting $*"
		echo "tar -zxvf $*" >> log.txt
		tar -zxvf $* >> log.txt
		if [ $? != 0 ]; then
			echo "Failed to extract $*"
			exit 1
		fi
	fi
}

#############################
# Actual build script
#############################
if [ "$BUILD_TARGET" = "none" ]; then
	echo "You need to specify a build target with:"
	echo "$0 win32"
	echo "$0 debian"
	exit 0
fi

# Change working directory to the directory the script is in
# http://stackoverflow.com/a/246128
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $SCRIPT_DIR

checkTool git "git: http://git-scm.com/"
checkTool curl "curl: http://curl.haxx.se/"
if [ $BUILD_TARGET = "win32" ]; then
	#Check if we have 7zip, needed to extract and packup a bunch of packages for windows.
	checkTool 7z "7zip: http://www.7-zip.org/"
fi

# Clean sources
rm -rf deb_dist
rm -rf win_dist

#############################
# Debian packaging
#############################

if [ $BUILD_TARGET = "debian" ]; then
	# Generate Debian source package
	python setup.py --command-packages=stdeb.command sdist_dsc \
	#--debian-version 1 \
	#--suite 'trusty' \
	#--section 'misc' \
	#--package 'web2board' \
	#--depends 'python,
	#           python-serial,
	#           avrdude \
	#bdist_deb # Used to generate deb files

	# Copy postinst and postrm files
	cp -a pkg/linux/debian/postinst deb_dist/web2board-${VERSION}/debian/postinst
	cp -a pkg/linux/debian/postrm deb_dist/web2board-${VERSION}/debian/postrm

	# Modify changelog and control files
	cp -a pkg/linux/debian/changelog deb_dist/web2board-${VERSION}/debian/changelog
	cp -a pkg/linux/debian/control deb_dist/web2board-${VERSION}/debian/control

	cd deb_dist/web2board-${VERSION}
	if [ $EXTRA_ARGS ]; then
		if [ $EXTRA_ARGS = "-s" ]; then
			# Build and sign Debian sources
			debuild -S -sa
		elif [ $EXTRA_ARGS = "-i" ]; then
			# Install Debian package
			dpkg-buildpackage
			sudo dpkg -i ../web2board*.deb
			sudo apt-get -f install
		elif [ $EXTRA_ARGS = "-u" ]; then
			# Upload to launchpad
			debuild -S -sa
			PPA=${PPA:="ppa:jesus-arroyo/web2board"}
			RELEASES="trusty utopic"
			ORIG_RELEASE=`head -1 pkg/linux/debian/changelog | sed 's/.*) \(.*\);.*/\1/'`
			cd .. ; mv web2board-${VERSION} web2board-${VERSION}${VEXT}
			mv web2board_${VERSION}.orig.tar.gz web2board_${VERSION}${VEXT}.orig.tar.gz
			cd web2board-${VERSION}${VEXT}
			for RELEASE in $RELEASES ;
			do
			  cp debian/changelog debian/changelog.backup
			  sed -i "s/${ORIG_RELEASE}/${RELEASE}/;s/${VERSION}/${VERSION}${VEXT}/;s/bq1/bq1~${RELEASE}1/" debian/changelog
			  debuild -S -sa
			  dput -f ${PPA} ../web2board_${VERSION}${VEXT}-bq1~${RELEASE}1_source.changes
			  mv debian/changelog.backup debian/changelog
			done
		fi
		else
			# Build and sign Debian package
			dpkg-buildpackage
		fi

	# Clean directory
	cd ../..
	rm -rf "Web2board.egg-info"
fi


#############################
# Rest
#############################

#############################
# Download all needed files.
#############################

if [ $BUILD_TARGET = "win32" ]; then
	mkdir -p win_dist
	cd win_dist
	# Get portable python for windows and extract it. (Linux and Mac need to install python themselfs)
	downloadURL http://ftp.nluug.nl/languages/python/portablepython/v2.7/PortablePython_${WIN_PORTABLE_PY_VERSION}.exe
	downloadURL http://sourceforge.net/projects/pyserial/files/pyserial/2.7/pyserial-2.7.win32.exe
fi

#############################
# Build the packages
#############################

if [ $BUILD_TARGET = "win32" ]; then
	rm -rf ${TARGET_DIR}
	mkdir -p ${TARGET_DIR}

	rm -f log.txt

	# For windows extract portable python to include it.
	extract PortablePython_${WIN_PORTABLE_PY_VERSION}.exe \$_OUTDIR/App
	extract PortablePython_${WIN_PORTABLE_PY_VERSION}.exe \$_OUTDIR/Lib/site-packages
	extract PortablePython_${WIN_PORTABLE_PY_VERSION}.exe \$_OUTDIR/dateutil
	extract pyserial-2.7.win32.exe PURELIB

	mkdir -p ${TARGET_DIR}/python
	mv \$_OUTDIR/App/* ${TARGET_DIR}/python
	mv \$_OUTDIR/Lib/site-packages/wx* ${TARGET_DIR}/python/Lib/site-packages
	mv \$_OUTDIR/dateutil ${TARGET_DIR}/python/Lib
	mv PURELIB/serial ${TARGET_DIR}/python/Lib
	
	rm -rf \$_OUTDIR
	rm -rf PURELIB
	rm -rf PLATLIB
	rm -rf Win32

	# Clean up portable python a bit, to keep the package size down.
	rm -rf ${TARGET_DIR}/python/PyScripter.*
	rm -rf ${TARGET_DIR}/python/Doc
	rm -rf ${TARGET_DIR}/python/locale
	rm -rf ${TARGET_DIR}/python/tcl
	rm -rf ${TARGET_DIR}/python/Lib/test
	rm -rf ${TARGET_DIR}/python/Lib/site-packages/wx-2.8-msw-unicode/wx/tools
	rm -rf ${TARGET_DIR}/python/Lib/site-packages/wx-2.8-msw-unicode/wx/locale
	#Remove the gle files because they require MSVCR71.dll, which is not included. We also don't need gle, so it's safe to remove it.
	rm -rf ${TARGET_DIR}/python/Lib/OpenGL/DLLS/gle*

	# Add Web2board
	mkdir -p ${TARGET_DIR}/doc ${TARGET_DIR}/res ${TARGET_DIR}/src
	#cp -a ../doc/* ${TARGET_DIR}/doc
	cp -a ../res/* ${TARGET_DIR}/res
	cp -a ../src/* ${TARGET_DIR}/src

	# Add script files
	cp -a ../pkg/${BUILD_TARGET}/*.bat $TARGET_DIR/

	# Package the result
	rm -rf ../pkg/win32/dist
	ln -sf `pwd`/${TARGET_DIR} ../pkg/win32/dist
	makensis -DVERSION=${VERSION}${VEXT} ../pkg/win32/installer.nsi
	if [ $? != 0 ]; then echo "Failed to package NSIS installer"; exit 1; fi
	mv ../pkg/win32/Web2board_${VERSION}${VEXT}.exe .
	rm -rf ../pkg/win32/dist
fi
