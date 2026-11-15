import sys


class ExactCounter:
    def __init__(self):
        self.ids = set()

    def add(self, visitor_id):
        if not isinstance(visitor_id, str):
            raise TypeError('visitor_id must be a string')
        self.ids.add(visitor_id)

    def update(self, visitor_ids):
        for visitor_id in visitor_ids:
            self.add(visitor_id)
        return self

    def estimate(self):
        return len(self.ids)

    def payload_bytes(self):
        return sum(sys.getsizeof(value) for value in self.ids)

    def memory_bytes(self):
        return sys.getsizeof(self) + sys.getsizeof(self.__dict__) + sys.getsizeof(self.ids) + self.payload_bytes()
