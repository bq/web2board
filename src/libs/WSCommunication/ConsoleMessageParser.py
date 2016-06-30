import logging


class ConsoleMessageParser:
    INIT = "_$INIT$_"
    END = "_$END$_"
    log = logging.getLogger(__name__)

    def __init__(self):
        self.buffer = ""

    def add_data(self, data):
        data = data if isinstance(data, str) else data.decode('utf-8')
        data = self.buffer + data

        messages = []
        messages_to_end = data.split(self.END)
        self.buffer = messages_to_end.pop(-1)

        for m2e in messages_to_end:
            try:
                messages.append(m2e.rsplit(self.INIT, 1)[1])
            except IndexError:
                self.log.exception("message corrupted (ignored)")

        return messages
