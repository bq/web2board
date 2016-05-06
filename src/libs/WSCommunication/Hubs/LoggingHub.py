from wshubsapi.hub import Hub


class LoggingHub(Hub):
    def __init__(self):
        super(LoggingHub, self).__init__()
        self.records_buffer = list()

    def get_all_buffered_records(self):
        return self.records_buffer