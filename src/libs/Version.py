import logging
import json

from libs.PathsManager import PathsManager


class Version:
    _log = logging.getLogger(__name__)
    web2board = None
    bitbloq_libs = None
    bitbloq_libs_libraries = []

    @classmethod
    def read_version_values(cls):
        try:
            cls._log.info("Reading config file")
            with open(PathsManager.VERSION_PATH) as f:
                version_object = json.load(f)
            cls.web2board = version_object["version"]
            cls.bitbloq_libs = version_object["bitbloqLibs"]["version"]
            cls.bitbloq_libs_libraries = version_object["bitbloqLibs"]["librariesNames"]
        except ValueError:
            cls._log.critical("version file corrupted, necessary to check!")

    @classmethod
    def store_values(cls):
        with open(PathsManager.CONFIG_PATH, "w") as f:
            values = dict(version=cls.web2board,
                          bitblowLibs=dict(version=cls.bitbloq_libs,
                                           librariesNames=cls.bitbloq_libs_libraries))
            json.dump(values, f, indent=4)

    @classmethod
    def log_data(cls):
        cls._log.info("web2board version: {}".format(cls.web2board))
        cls._log.info("bitbloqLibs version: {}".format(cls.bitbloq_libs))
        cls._log.info("bitbloqLibs libraries: {}".format(cls.bitbloq_libs_libraries))



