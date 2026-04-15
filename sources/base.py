class BaseSource:

    def fetch(self):
        raise NotImplementedError

    def normalize(self, raw):
        raise NotImplementedError