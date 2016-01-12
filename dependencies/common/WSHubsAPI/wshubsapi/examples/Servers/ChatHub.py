# -*- coding: utf-8 -*-
from wshubsapi.Hub import Hub


class ChatHub(Hub):
    def sendToAll(self, name, _sender, message):  # _sender is an automatically passed argument
        ### we can call a sender's function in a intuitive way (the function has to be defined in the client):
        # _sender.onMessage(name,message)
        ###call function from all clients
        # self.allClients.onMessage(name,message)
        ###call function from all clients but the sender
        otherClients = self.getClientsHolder().getOtherClients(_sender[0])
        otherClients.onMessage(name, message)
        _sender.onMessage("sender", message)
        ### or call function from a selection of clients
        # self.getClients(lambda x:x.ID > 4).onMessage(name,message)
        return len(otherClients)

    @staticmethod
    def static():
        pass

    @classmethod
    def classMethod(cls):
        pass
