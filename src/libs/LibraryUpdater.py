#!/usr/bin/python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------#
#                                                                       #
# This file is part of the web2board project                            #
#                                                                       #
# Copyright (C) 2015 Mundo Reader S.L.                                  #
#                                                                       #
# Date: November 2015                                                   #
# Author: Irene Sanz Nieto <irene.sanz@bq.com>                          #
#                                                                       #
#-----------------------------------------------------------------------#
from urllib2 import urlopen, URLError, HTTPError
import shutil, platform, sys, os, json, zipfile, distutils
from Arduino import base
from distutils.dir_util import mkpath


##
# Class LibraryUpdater, created to check for downloaded libraries and update them if necessary
#
class LibraryUpdater:
	def __init__(self):
		# Select Sketchbook folder depending on OS
		if platform.system() == 'Linux':
			# self.pathToSketchbook = expanduser("~").decode('latin1')+'/Arduino/libraries'
			self.pathToSketchbook = base.sys_path.get_home_path()+'/Arduino'

		elif platform.system() == 'Windows' or platform.system() == 'Darwin':
			# self.pathToSketchbook = expanduser("~").decode('latin1')+'/Documents/Arduino/libraries'
			self.pathToSketchbook = base.sys_path.get_document_path()+'/Arduino'


		self.pathToMain = sys.path[0]
		if platform.system() == 'Darwin':
			if os.environ.get('PYTHONPATH') != None:
				self.pathToMain = os.environ.get('PYTHONPATH')	

	def getBitbloqLibsVersion(self):
		# Get bitbloqLibs version from config file
		if not os.path.isfile(base.sys_path.get_home_path()+'/.web2boardconfig'):
				shutil.copyfile(self.pathToMain+'/res/config.json', base.sys_path.get_home_path()+'/.web2boardconfig')
		with open(base.sys_path.get_home_path()+'/.web2boardconfig') as json_data_file:
			data = json.load(json_data_file)
			version = str(data['bitbloqLibsVersion'])
		return version

	def getBitbloqLibsName(self):
		# Get bitbloqLibs name from config file
		if not os.path.isfile(base.sys_path.get_home_path()+'/.web2boardconfig'):
			shutil.copyfile(self.pathToMain+'/res/config.json', base.sys_path.get_home_path()+'/.web2boardconfig')
		with open(base.sys_path.get_home_path()+'/.web2boardconfig') as json_data_file:
			data = json.load(json_data_file)
			bitbloqLibsName = []
			try:
				bitbloqLibsName = data['bitbloqLibsName']
			except:
				print 'No bitbloqLibsName'
				pass
		return bitbloqLibsName

	def setBitbloqLibsVersion(self, newVersion):
		if not os.path.isfile(base.sys_path.get_home_path()+'/.web2boardconfig'):
			shutil.copyfile(self.pathToMain+'/res/config.json', base.sys_path.get_home_path()+'/.web2boardconfig')
		jsonFile = open(base.sys_path.get_home_path()+'/.web2boardconfig', "r")
		data = json.load(jsonFile)
		jsonFile.close()

		data["bitbloqLibsVersion"] = newVersion

		jsonFile = open(base.sys_path.get_home_path()+'/.web2boardconfig', "w+")
		jsonFile.write(json.dumps(data))
		jsonFile.close()


	def setBitbloqLibsNames(self, bitbloqLibsNames):
		if not os.path.isfile(base.sys_path.get_home_path()+'/.web2boardconfig'):
			shutil.copyfile(self.pathToMain+'/res/config.json', base.sys_path.get_home_path()+'/.web2boardconfig')
		jsonFile = open(base.sys_path.get_home_path()+'/.web2boardconfig', "r")
		data = json.load(jsonFile)
		jsonFile.close()

		data["bitbloqLibsName"] = bitbloqLibsNames

		jsonFile = open(base.sys_path.get_home_path()+'/.web2boardconfig', "w+")
		jsonFile.write(json.dumps(data))
		jsonFile.close()

	def downloadFile(self, url, path='.'):
	    # Open the url
	    try:
	        f = urlopen(url)
	        print "downloading " + url

	        # Open our local file for writing
	        with open(base.sys_path.get_tmp_path()+'/'+os.path.basename(url), "wb") as local_file:
	            local_file.write(f.read())

	    #handle errors
	    except HTTPError, e:
	        print "HTTP Error:", e.code, url
	    except URLError, e:
	        print "URL Error:", e.reason, url

	def downloadLibs (self):
		version = self.getBitbloqLibsVersion()
		print ('Downloading new libs, version', version)

		# Download bitbloqLibs
		url = ('https://github.com/bq/bitbloqLibs/archive/v'+version+'.zip')
		self.downloadFile(url)

		# Extract it to the correct dir
		with zipfile.ZipFile(base.sys_path.get_tmp_path()+'/'+'v'+version+'.zip', "r") as z:
			z.extractall(base.sys_path.get_tmp_path())

		tmp_path = base.sys_path.get_tmp_path()+'/bitbloqLibs-'+version
		if int(version.replace('.','')) <= 2:
			distutils.dir_util.copy_tree(tmp_path, self.pathToSketchbook+'/libraries/bitbloqLibs')
			bitbloqLibsNames = 'bitbloqLibs'
		elif int(version.replace('.','')) > 2:
			for name in os.listdir(tmp_path):
				if os.path.isdir(tmp_path+'/'+name):
					distutils.dir_util.copy_tree(tmp_path, self.pathToSketchbook+'/libraries/')
					#shutil.copytree(tmp_path, self.pathToSketchbook+'/libraries/'+name)
			bitbloqLibsNames = [ name for name in os.listdir(base.sys_path.get_tmp_path()+'/bitbloqLibs-'+version) if os.path.isdir(os.path.join(base.sys_path.get_tmp_path()+'/bitbloqLibs-'+version, name)) ]

		# Store the names of the bitbloq libraries
		self.setBitbloqLibsNames(bitbloqLibsNames)

		# Remove .zip
		try:
		   os.remove(base.sys_path.get_tmp_path()+'/'+'v'+version+'.zip')
		except OSError:
		   pass

	def  libExists(self):
		missingLibs = False
		libsNames = self.getBitbloqLibsName()
		if not os.path.exists(self.pathToSketchbook):
			os.makedirs(self.pathToSketchbook)
		if len(libsNames) < 1:
			missingLibs = True
		else:
			if(libsNames == 'bitbloqLibs'):
				libsNames = ['bitbloqLibs']
			for lib in libsNames:
				if not os.path.exists(self.pathToSketchbook+'/libraries/'+lib) or not os.listdir(self.pathToSketchbook+'/libraries/'+lib):
					missingLibs = True

		# If there is no bitbloqLibs folder or it is empty
		# if not os.path.exists(self.pathToSketchbook+'/bitbloqLibs') or not os.listdir(self.pathToSketchbook+'/bitbloqLibs'):
		# 	missingLibs = True

		if missingLibs:
			self.downloadLibs()
