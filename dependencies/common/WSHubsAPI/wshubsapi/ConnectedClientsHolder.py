from wshubsapi.ConnectedClientsGroup import ConnectedClientsGroup


class ConnectedClientsHolder:
    allConnectedClients = dict()

    def __init__(self, hubName):
        self.hubName = hubName

    def getAllClients(self):
        return ConnectedClientsGroup(list(self.allConnectedClients.values()), self.hubName)

    def getOtherClients(self, sender):
        """
        :type sender: ConnectedClientsGroup
        """
        return ConnectedClientsGroup([c for c in self.allConnectedClients.values() if c.ID != sender[0].ID], self.hubName)

    def getClients(self, filterFunction):
        return ConnectedClientsGroup([c for c in self.allConnectedClients.values() if filterFunction(c)], self.hubName)

    def getClient(self, clientId):
        return ConnectedClientsGroup([self.allConnectedClients[clientId]], self.hubName)

    @classmethod
    def appendClient(cls, client):
        cls.allConnectedClients[client.ID] = client

    @classmethod
    def popClient(cls, clientId):
        """
        :type clientId: str|int
        """
        return cls.allConnectedClients.pop(clientId, None)
