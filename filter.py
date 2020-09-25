class Filter:
    def __init__(self):
        self.sqldata = {}

    def url_data(self, cn):
        for i,k in enumerate(cn):
            self.sqldata[i] = k
        return self.sqldata

