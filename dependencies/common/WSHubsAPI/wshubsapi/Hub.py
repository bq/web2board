from wshubsapi.ConnectedClientsHolder import ConnectedClientsHolder

__author__ = 'Jorge'

class UnsuccessfulReplay:
    def __init__(self, replay):
        self.replay = replay

class HubException(Exception):
    pass


class Hub(object):
    HUBs_DICT = {}

    def __init__(self):
        hubName = self.__class__.__dict__.get("__HubName__", self.__class__.__name__)
        if hubName in self.HUBs_DICT:
            raise HubException("Hub's name must be unique")
        if hubName.startswith("__"):
            raise HubException("Hub's name can not start with '__'")
        if hubName == "wsClient":
            raise HubException("Hub's name can not be 'wsClient', it is a  reserved name")
        setattr(self.__class__, "__HubName__", hubName)
        self.HUBs_DICT[hubName] = self

        self.__class__._clientsHolder = ConnectedClientsHolder(hubName)

    @classmethod
    def getClientsHolder(cls):
        """
        :rtype: ConnectedClientsHolder
        """
        return cls._clientsHolder

    def _constructUnsuccessfulReplay(self, replay):
        return UnsuccessfulReplay(replay)
