# Comprehensive Test Suite for AGT Designer

This directory contains comprehensive tests for the AGT Designer application.

## Test Structure

The test suite is organized into the following modules:

- **`conftest.py`**: Pytest configuration and shared fixtures
- **`test_api_endpoints.py`**: Tests for all Flask API endpoints
- **`test_product_database.py`**: Tests for ProductDatabase class and database operations
- **`test_excel_processing.py`**: Tests for Excel file processing and data extraction
- **`test_product_matching.py`**: Tests for JSON matcher, database matcher, and matching logic
- **`test_template_generation.py`**: Tests for template processing and label generation
- **`test_session_management.py`**: Tests for session management and persistence
- **`test_data_validation.py`**: Tests for data validation, normalization, and formatting
- **`test_integration.py`**: Integration tests for end-to-end workflows

## Running Tests

### Prerequisites

Install pytest and required dependencies:

```bash
pip install pytest pytest-cov pytest-mock
```

### Run All Tests

```bash
pytest
```

### Run Specific Test Module

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

### Run with Coverage

```bash
pytest --cov=core --cov=src --cov-report=html
```

### Run with Verbose Output

```bash
pytest -v
```

### Run Only Fast Tests

```bash
pytest -m "not slow"
```

## Test Categories

Tests are organized by functionality:

### API Endpoints (`test_api_endpoints.py`)
- Status endpoint
- Store management endpoints
- Tag management endpoints
- Template endpoints
- Lineage endpoints
- Session endpoints
- Upload endpoints
- Generation endpoints
- Database endpoints

### Product Database (`test_product_database.py`)
- Database initialization
- Product CRUD operations
- Search and matching
- Lineage management
- Caching functionality
- Concurrency handling

### Excel Processing (`test_excel_processing.py`)
- File loading
- Data extraction
- Field mapping
- Data validation
- Normalization
- Error handling

### Product Matching (`test_product_matching.py`)
- JSON matcher
- Enhanced JSON matcher
- Advanced matcher
- AI matcher
- Matching validation
- SKU matching
- Deduplication

### Template Generation (`test_template_generation.py`)
- Template processing
- Formatting
- Text processing
- Marker processing
- Template types
- Cell formatting
- Fast generation

### Session Management (`test_session_management.py`)
- Session creation
- Data storage
- Change tracking
- Statistics
- Persistence
- Concurrency
- Cleanup

### Data Validation (`test_data_validation.py`)
- Field mapping
- Weight normalization
- Price validation
- THC/CBD validation
- Product type validation
- Lineage validation
- Vendor validation
- SKU validation
- Deduplication

### Integration Tests (`test_integration.py`)
- Excel to database flow
- Matching to generation flow
- Session to generation flow
- Database update flow
- Error handling flow
- Performance flow

## Fixtures

Common fixtures are defined in `conftest.py`:

- `test_data_dir`: Temporary directory for test data
- `temp_db`: Temporary SQLite database
- `populated_db`: Database with sample products
- `sample_excel_file`: Sample Excel file for testing
- `sample_excel_data`: Sample Excel data as dictionary
- `sample_products`: Sample product data
- `sample_json_product`: Sample JSON product for matching
- `mock_flask_app`: Mock Flask application
- `mock_session`: Mock Flask session
- `mock_excel_processor`: Mock Excel processor

## Writing New Tests

When adding new tests:

1. Follow the existing test structure and naming conventions
2. Use appropriate fixtures from `conftest.py`
3. Mark slow tests with `@pytest.mark.slow`
4. Mark integration tests with `@pytest.mark.integration`
5. Use `pytest.skip()` for tests that require unavailable dependencies
6. Add docstrings explaining what each test validates

## Test Coverage Goals

- **Unit Tests**: 80%+ coverage for core modules
- **Integration Tests**: Cover all major workflows
- **API Tests**: Cover all endpoints
- **Error Handling**: Test error cases and edge cases

## Continuous Integration

Tests should be run:
- Before committing code
- In CI/CD pipeline
- Before deploying to production

## Notes

- Some tests may skip if dependencies are not available (e.g., Flask context, database)
- Tests use temporary files and databases that are cleaned up automatically
- Mock objects are used where appropriate to isolate units under test
- Integration tests may require actual database setup

