from wshubsapi.ClientFileGenerator.JAVAFileGenerator import JAVAFileGenerator
from wshubsapi.ClientFileGenerator.JSClientFileGenerator import JSClientFileGenerator
from wshubsapi.ClientFileGenerator.PythonClientFileGenerator import PythonClientFileGenerator
from wshubsapi.Hub import Hub


class HubsInspectorException(Exception):
    pass


class HubsInspector:
    __hubsConstructed = False

    @classmethod
    def inspectImplementedHubs(cls, forceReconstruction=False):
        if not cls.__hubsConstructed or forceReconstruction:
            Hub.HUBs_DICT.clear()
            for hubClass in Hub.__subclasses__():
                try:
                    hubClass()
                except TypeError as e:
                    if "__init__()" in str(e):
                        raise HubsInspectorException(
                            "Hubs can not have a constructor with parameters. Check Hub: %s" % hubClass.__name__)
                    else:
                        raise e
            cls.__hubsConstructed = True

    @classmethod
    def constructJSFile(cls, path="."):
        cls.inspectImplementedHubs()
        JSClientFileGenerator.createFile(path, Hub.HUBs_DICT.values())

    @classmethod
    def constructJAVAFile(cls, package, path="."):
        cls.inspectImplementedHubs()
        hubs = Hub.HUBs_DICT.values()
        JAVAFileGenerator.createFile(path, package, hubs)
        JAVAFileGenerator.createClientTemplate(path, package, hubs)

    @classmethod
    def constructPythonFile(cls, path="."):
        cls.inspectImplementedHubs()
        PythonClientFileGenerator.createFile(path, Hub.HUBs_DICT.values())

    @classmethod
    def getHubInstance(cls, hubClass):
        return Hub.HUBs_DICT[hubClass.__HubName__]
