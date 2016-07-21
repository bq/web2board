import logging
import json

from libs.PathsManager import PathsManager


class VersionError(Exception):
    pass


class Version:
    def __init__(self, version_string):
        self.version_string = version_string
        """:type : str """
        self.parse_version_string(version_string)

    @property
    def version_numbers(self):
        return self.parse_version_string(self.version_string)

    @staticmethod
    def parse_version_string(version_string):
        try:
            return [int(n) for n in version_string.split(".")]
        except (ValueError, AttributeError):
            raise VersionError("Bad format version: {}".format(version_string))

    def set_version_values(self, version_string):
        self.parse_version_string(version_string)
        self.version_string = version_string

    def __eq__(self, version_string):
        self.parse_version_string(version_string)
        return self.version_string == version_string

    def __ne__(self, version_string):
        self.parse_version_string(version_string)
        return self.version_string != version_string

    def __gt__(self, version_string):
        return self.version_numbers > self.parse_version_string(version_string)

    def __ge__(self, version_string):
        return self > version_string or self == version_string

    def __lt__(self, version_string):
        return self.version_numbers < self.parse_version_string(version_string)

    def __le__(self, version_string):
        return self < version_string or self == version_string


class LibsVersion(Version):
    def __init__(self, version_string, libraries_names=None, url=""):
        Version.__init__(self, version_string)
        self.libraries_names = list() if libraries_names is None else libraries_names
        self.url = url

    def set_version_values(self, version_values):
        Version.set_version_values(self, version_values["version"])
        try:
            self.libraries_names= [l.encode("utf-8") for l in version_values["librariesNames"]]
        except UnicodeError:
            self.libraries_names = version_values["librariesNames"]
        self.url=version_values["url"]

    def get_version_values(self):
        return dict(version=self.version_string,
                    librariesNames=self.libraries_names,
                    url=self.url)

    def compare_libraries_names(self, libs_names):
        """
        :type other: LibsVersion
        """
        return set(self.libraries_names) == set(libs_names)


class AppVersion:
    _log = logging.getLogger("AppVersion")
    web2board = Version("0.0.0")
    libs = LibsVersion("0.0.0")

    @classmethod
    def read_version_values(cls):
        try:
            cls._log.info("Reading config file")
            with open(PathsManager.VERSION_PATH) as f:
                version_object = json.load(f)
            cls.web2board.set_version_values(version_object["version"])
            cls.libs.set_version_values(version_object["libs"])
        except (ValueError, VersionError):
            cls._log.critical("version file corrupted, necessary to check!")

    @classmethod
    def store_values(cls):
        with open(PathsManager.VERSION_PATH, "w") as f:
            values = dict(version=cls.web2board.version_string,
                          libs=cls.libs.get_version_values())
            json.dump(values, f, indent=4, ensure_ascii=False)

    @classmethod
    def log_data(cls):
        cls._log.info("web2board version: {}".format(cls.web2board.version_string))
        cls._log.info("libs version: {}".format(cls.libs.version_string))
        cls._log.info("libs libraries: {}".format(cls.libs.libraries_names))
        cls._log.info("libs url: {}".format(cls.libs.url))

