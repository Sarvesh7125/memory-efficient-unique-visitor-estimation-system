import hashlib
import math
import sys


class HyperLogLog:
    def __init__(self, p=12):
        if type(p) is not int or not 4 <= p <= 18:
            raise ValueError('p must be an integer between 4 and 18')
        self.p = p
        self.m = 1 << p
        self.registers = bytearray(self.m)

    def add(self, visitor_id):
        if not isinstance(visitor_id, str):
            raise TypeError('visitor_id must be a string')
        h = int.from_bytes(hashlib.blake2b(visitor_id.encode('utf-8'), digest_size=8).digest(), 'big')
        q = 64 - self.p
        index = h >> q
        remainder = h & ((1 << q) - 1)
        rank = q - remainder.bit_length() + 1
        if rank > self.registers[index]:
            self.registers[index] = rank

    def update(self, visitor_ids):
        for visitor_id in visitor_ids:
            self.add(visitor_id)
        return self

    def estimate(self):
        m = self.m
        alpha = {16: 0.673, 32: 0.697, 64: 0.709}.get(m, 0.7213 / (1 + 1.079 / m))
        raw = alpha * m * m / math.fsum(2.0 ** -r for r in self.registers)
        zeros = self.registers.count(0)
        if raw <= 2.5 * m and zeros:
            return m * math.log(m / zeros)
        return raw

    def merge(self, other):
        if not isinstance(other, HyperLogLog) or self.p != other.p:
            raise ValueError('Both sketches must have the same precision')
        for i, rank in enumerate(other.registers):
            if rank > self.registers[i]:
                self.registers[i] = rank
        return self

    @property
    def theoretical_rse(self):
        return 1.04 / math.sqrt(self.m)

    def payload_bytes(self):
        return len(self.registers)

    def memory_bytes(self):
        return sys.getsizeof(self) + sys.getsizeof(self.__dict__) + sys.getsizeof(self.registers) + sys.getsizeof(self.p) + sys.getsizeof(self.m)
