from logging import Handler


class ArrayHandler(Handler):
    def __init__(self, max_count=20):
        self.records = []
        self.max_count = max_count
        Handler.__init__(self)

    def emit(self, record):
        try:
            msg = self.format(record)
            self.records.append(msg)
            if len(self.records) > self.max_count:
                del(self.records[0])
        except Exception:
            self.handleError(record)

    def logs(self):
        return self.records
