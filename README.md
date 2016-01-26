[![Stories in Ready](https://badge.waffle.io/bq/web2board.png?label=ready&title=Ready)](https://waffle.io/bq/web2board)
# web2board
Native program that connects a website and a Arduino compatible board. It compiles Arduino sketches and uploads them onto a board.


This project has been developed in Python language and it is distributed under GPL v3 license.


Special Thanks
======================

* Arduino founders & staff (http://www.arduino.cc/) for creating all the Arduino Core that is widely used nowadays.
* Akkana Peck <akkana@shallowsky.com> for the Makefile-arduino v0.8 in which our Makefile is based.
* DP <https://github.com/opiate> for its great SimpleWebSocketServer library for python.


# Installing

### GNU/Linux Ubuntu

Download and install "web2board.deb"

If user has no access to serial port, execute:

```bash
sudo usermod -a -G dialout $USER
```

Logout from your session to apply the changes

```bash
logout
```

### Windows

[TODO]


# Development

web2board has been developed in [Ubuntu Gnome](http://ubuntugnome.org/). If you are a developer and you want to modify the code, contribute, build packages, etc. you may follow this steps:

## 1. Set up the environment

### Tools

#### Sublime Text 3 IDE
```bash
sudo add-apt-repository ppa:webupd8team/sublime-text-3
sudo apt-get update
sudo apt-get install sublime-text-installer
```

#### Arduino IDE
```bash
sudo apt-get install arduino arduino-core
```

#### Git version control
```bash
sudo apt-get install git gitk
```

### Dependencies

Following dependencies are included in deb package, but if you want to install it manually, they are:

#### Python
```bash
sudo apt-get install python-serial 
```

#### AVRDUDE
```bash
sudo apt-get install avrdude
```

In order to generate Debian and Windows packages, some extra dependencies are needed

#### Packaging
```bash
sudo apt-get install build-essential pkg-config python-dev python-stdeb p7zip-full curl nsis
```

## 2. Download source code

All source code is available on GitHub. You can download main web2board project by doing:

### web2board

```bash
git clone git@github.com:bq/web2board.git
```

## 3. Execute source code

In the project directory, execute the command:

```bash
python src/web2board.py
```

## 4. Build packages

web2board development comes with a script "package.sh", this script has been designed to run under *nix OSes (Linux, MacOS). For Windows the package.sh script can be run from bash using git.
The "package.sh" script generates a final release package. You should not need it during development, unless you are changing the release process. If you want to distribute your own version of web2board, then the package.sh script will allow you to do that.

### GNU/Linux Ubuntu
```bash
bash package.sh debian     # Generate deb package
bash package.sh debian -s  # Generate sources
bash package.sh debian -i  # Install deb package
bash package.sh debian -u  # Upload to launchpad
```

### Windows
```bash
bash package.sh win32  # Generate exe package
```

### GNU/Linux Fedora

[TODO]

### Mac OS X

[TODO]
