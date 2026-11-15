import hashlib
import math
import pytest
from src.exact import ExactCounter
from src.hyperloglog import HyperLogLog
from scripts.verify_algorithms import compare
from src.paths import ROOT


@pytest.mark.parametrize('p', [4, 8, 10, 12, 14, 16, 18])
def test_empty(p):
    h = HyperLogLog(p)
    assert h.estimate() == 0
    assert h.payload_bytes() == 2 ** p
    assert h.theoretical_rse == 1.04 / math.sqrt(2 ** p)


@pytest.mark.parametrize('p', [3, 19, 12.0, True, '12'])
def test_invalid_precision(p):
    with pytest.raises(ValueError):
        HyperLogLog(p)


def test_exact_and_duplicates():
    ids = ['001', '1', '001', '世界', '']
    assert ExactCounter().update(ids).estimate() == 4
    h = HyperLogLog().update(ids)
    before = h.registers[:]
    h.update(ids * 100)
    assert h.registers == before
    assert abs(h.estimate() - 4) < 0.1


@pytest.mark.parametrize('cls', [ExactCounter, HyperLogLog])
def test_type(cls):
    with pytest.raises(TypeError):
        cls().add(123)


def test_hash_index_and_rank():
    h = HyperLogLog(12)
    value = int.from_bytes(hashlib.blake2b(b'visitor', digest_size=8).digest(), 'big')
    bits = format(value, '064b')
    suffix = bits[12:]
    expected_rank = len(suffix) - len(suffix.lstrip('0')) + 1
    h.add('visitor')
    assert h.registers[int(bits[:12], 2)] == expected_rank
    assert sum(r != 0 for r in h.registers) == 1


def test_all_zero_suffix(monkeypatch):
    class FakeHash:
        def digest(self):
            return bytes(8)
    monkeypatch.setattr(hashlib, 'blake2b', lambda *a, **kw: FakeHash())
    h = HyperLogLog(12)
    h.add('a')
    assert h.registers[0] == 53


@pytest.mark.parametrize('n', [100, 1000, 10000, 100000])
def test_accuracy(n):
    h = HyperLogLog().update(f'visitor-{i}' for i in range(n))
    assert abs(h.estimate() - n) / n < 0.08


def test_merge():
    a = [f'u{i}' for i in range(10000)]
    b = [f'u{i}' for i in range(5000, 15000)]
    left = HyperLogLog().update(a)
    right = HyperLogLog().update(b)
    expected = HyperLogLog().update(a + b)
    snapshot = right.registers[:]
    assert left.merge(right).registers == expected.registers
    assert right.registers == snapshot
    assert left.merge(left).registers == expected.registers
    assert right.merge(HyperLogLog()).registers == snapshot
    assert HyperLogLog().update(b).merge(HyperLogLog().update(a)).registers == expected.registers
    with pytest.raises(ValueError):
        left.merge(HyperLogLog(10))


def test_memory():
    h, exact = HyperLogLog(), ExactCounter()
    h_before = h.memory_bytes()
    e_before = exact.memory_bytes()
    h.update(str(i) for i in range(10000))
    exact.update(str(i) for i in range(10000))
    assert h.memory_bytes() == h_before
    assert exact.memory_bytes() > e_before
    assert exact.memory_bytes() > h.memory_bytes()


def test_csv_integration():
    result = compare(ROOT / 'data' / 'benchmark' / 'events_1000.csv')
    assert result['events'] == 1000
    assert result['exact_count'] == 250
    assert result['absolute_error_pct'] < 8
