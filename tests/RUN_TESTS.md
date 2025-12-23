# How to Run Tests

## Quick Start

### Install Test Dependencies
```bash
pip install -r tests/requirements.txt
```

Or install individually:
```bash
pip install pytest pytest-timeout pytest-mock
```

### Run All Tests
```bash
pytest
```

### Run Specific Test File
```bash
pytest tests/test_api_endpoints.py
```

### Run Specific Test Class
```bash
pytest tests/test_api_endpoints.py::TestStatusEndpoint
```

### Run Specific Test Function
```bash
pytest tests/test_api_endpoints.py::TestStatusEndpoint::test_status_endpoint_exists
```

### Run with Verbose Output
```bash
pytest -v
```

### Run Only Fast Tests (Skip Slow Ones)
```bash
pytest -m "not slow"
```

### Run with Timeout Protection
```bash
pytest --timeout=10
```

### Show Skipped Tests
```bash
pytest -rs
```

### Run Tests in Parallel (if pytest-xdist installed)
```bash
pytest -n auto
```

## Common Issues

### If pytest command not found:
```bash
python -m pytest
```

### If tests timeout:
Tests have a default 10-second timeout. Increase if needed:
```bash
pytest --timeout=30
```

### If coverage fails:
Coverage is optional. Tests will run without it. To enable:
```bash
pip install pytest-cov
pytest --cov=core --cov=src --cov-report=html
```

## Test Output

- `.` = test passed
- `F` = test failed
- `s` = test skipped
- `x` = test expected to fail but passed

