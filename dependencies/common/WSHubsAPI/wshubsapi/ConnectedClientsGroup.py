from wshubsapi import utils


class ConnectedClientsGroup:
    def __init__(self, connectedClientsInGroup, hubName):
        """
        :type connectedClientsInGroup: list of ConnectedClient
        """
        self.hubName = hubName
        self.connectedClients = connectedClientsInGroup

    def append(self, connectedClient):
        """
        :type connectedClient: ConnectedClient.ConnectedClient
        """
        self.connectedClients.append(connectedClient)

    def __getattr__(self, item):
        """
        :param item: function name defined in the client side ("item" name keep because it is a magic function)
        """
        functions = []
        for c in self.connectedClients:
            functions.append(self.__constructFunctionToSendMessageToClient(c, item))

        def connectionFunctions(*args):
            for f in functions:
                f(*args)

        return connectionFunctions

    def __getitem__(self, item):
        """
        :rtype : ConnectedClient
        """
        return self.connectedClients.__getitem__(item)

    def __len__(self):
        return self.connectedClients.__len__()

    def __constructFunctionToSendMessageToClient(self, connectedClient, functionName):
        def connectionFunction(*args):
            message = {"function": functionName, "args": list(args), "hub": self.hubName}
            msgStr = utils.serializeMessage(connectedClient.pickler, message)
            connectedClient.writeMessage(msgStr)

        return connectionFunction

    def __iter__(self):
        for x in self.connectedClients:
            yield x
