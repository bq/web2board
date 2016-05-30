# web2board
Native program that connects a website and a Arduino compatible board. It compiles Arduino sketches and uploads them onto a board.


This project has been developed in Python language and it is distributed under GPL v3 license.


Special Thanks
======================

* Arduino founders & staff (http://www.arduino.cc/) for creating all the Arduino Core that is widely used nowadays.
* Akkana Peck <akkana@shallowsky.com> for the Makefile-arduino v0.8 in which our Makefile is based.
* Platformio  team <http://platformio.org/> for its great cross-platform build system.


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
# in web2board path
sudo pip install -r requirements.txt
```

#### AVRDUDE
```bash
sudo apt-get install avrdude
```

In order to generate Debian and Windows packages, some extra dependencies are needed

#### Packaging
```bash
# in web2board path
# set up res folder (only once)
python src/Scripts/ConstructRes.py
# start packaging
python src/Scripts/package.py

# installer will be created in installer folder
```

it is not possible to generate an installer for other platform other that the host due to a limitation in pyinstaller, see: http://pyinstaller.readthedocs.io/en/stable/usage.html?highlight=virtualbox#supporting-multiple-platforms
## 2. Download source code

All source code is available on GitHub. You can download main web2board project by doing:

### web2board

```bash
git clone git@github.com:bq/web2board.git
```

## 3. Execute source code

In the project directory, execute the command:

```bash
# in web2board path
# set up res folder (only once)
python src/Scripts/ConstructRes.py
# start web2board
python src/web2board.py
```

### GNU/Linux Fedora

[TODO]

