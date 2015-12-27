from libs.Packagers.LinuxPackager import LinuxPackager
from libs.Packagers.WindowsPackager import WindowsPackager

# packager = WindowsPackager()
packager = LinuxPackager()
packager.createPackage()

