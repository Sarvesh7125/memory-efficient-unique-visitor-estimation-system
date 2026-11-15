from io import BytesIO
from src.dashboard import analyze, columns, merge_demo, benchmark_dir


def test_upload_and_count():
    data = BytesIO(b'id,page\n001,a\n002,b\n001,c\nnull,d\n')
    assert columns(data) == ['id','page']
    result = analyze(data,'id')
    assert result['events'] == 3
    assert result['exact_count'] == 2
    assert abs(result['hll_estimate']-2) < 0.01


def test_hll_only():
    result = analyze(BytesIO(b'id\na\nb\n'),'id',8,False)
    assert result['exact_count'] is None
    assert result['exact_retained_bytes'] is None
    assert result['hll_register_bytes'] == 256


def test_empty():
    result = analyze(BytesIO(b'id\n'),'id')
    assert result['hll_estimate'] == 0
    assert result['absolute_error_pct'] is None


def test_merge():
    result = merge_demo(1000,2000,500)
    assert result['exact_union'] == 2500
    assert result['identical_registers']


def test_benchmarks():
    assert benchmark_dir() is None or (benchmark_dir()/'scalability.csv').exists()
