from libs.Packagers.LinuxPackager import LinuxPackager
from libs.Packagers.Packager import Packager
from libs.Packagers.WindowsPackager import WindowsPackager
from libs.Packagers.MacPackager import MacPackager

# packager = WindowsPackager()
# packager = LinuxPackager()

packager = Packager.constructCurrentPlatformPackager()
packager.createPackage()

