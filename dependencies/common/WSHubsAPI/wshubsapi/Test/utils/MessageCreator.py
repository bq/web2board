class MessageCreator:
    @classmethod
    def createReplayMessage(cls, **kwargs):
        message = cls.__getDefaultReplayMessage()
        message.update(kwargs)
        return message

    @classmethod
    def __getDefaultReplayMessage(cls):
        return {
            "success": True,
            "replay": "successfully completed",
            "hub": "TestHub",
            "function": "testFunction",
            "ID": 0
        }

    @classmethod
    def createOnMessageMessage(cls, **kwargs):
        message = cls.__getDefaultOnMessageMessage()
        message.update(kwargs)
        return message

    @classmethod
    def __getDefaultOnMessageMessage(cls):
        return {
            "hub": "TestHub",
            "function": "testFunction",
            "args": [1, "2"],
            "ID": 0
        }
