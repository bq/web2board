import os

from platformio import util
from platformio.pkgmanager import PackageManager
from platformio.platforms.base import PlatformFactory

os.chdir("Test/resources/platformio")

config = util.get_project_config()
section = config.sections()[0]
envOptions = config.items(section)
envOptions = {x[0]:x[1] for x in envOptions}
platform = PlatformFactory.newPlatform(envOptions["platform"])

platform.configure_default_packages(envOptions, ["upload"])
platform._install_default_packages()

pm = PackageManager()
pm.install("tool-avrdude")