from wshubsapi.Hub import Hub


class LoggingHub(Hub):
    def __init__(self):
        super(LoggingHub, self).__init__()
        self.recordsBuffer = list()

    def getAllBufferedRecords(self):
        return self.recordsBuffer