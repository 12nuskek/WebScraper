# WebScraper Test Suite

This directory contains comprehensive tests for the WebScraper project, organized with one file per object as requested.

## Test Structure

- **`test_core.py`** - Core application tests and base test utilities
- **`test_user_model.py`** - Tests for User model and UserManager
- **`test_profile_model.py`** - Tests for Profile model
- **`test_project_model.py`** - Tests for Project model
- **`test_account_views.py`** - Tests for account-related views
- **`test_project_views.py`** - Tests for project-related views
- **`test_account_serializers.py`** - Tests for account serializers
- **`test_project_serializers.py`** - Tests for project serializers

## Running Tests

### Option 1: Using Django's manage.py (Recommended)
```bash
cd scraping-backend
python manage.py test tests
```

### Option 2: Using the custom test runner
```bash
# From project root
python tests/run_tests.py

# Run specific test file
python tests/run_tests.py test_user_model

# Run with verbose output
python tests/run_tests.py -v 2
```

### Option 3: Using pytest (if installed)
```bash
cd scraping-backend
pytest ../tests/
```

## Test Coverage

The test suite covers:

### Models
- ✅ User model and custom UserManager
- ✅ Profile model with relationships and methods
- ✅ Project model with relationships and constraints

### Views
- ✅ User registration and authentication
- ✅ JWT token handling (login/logout)
- ✅ Profile management (CRUD operations)
- ✅ Project management (CRUD operations)
- ✅ Permission classes (IsOwner)

### Serializers
- ✅ User registration serializer with validation
- ✅ Profile serializer with nested user data
- ✅ Project serializer with field validation

### Core Functionality
- ✅ Django configuration and setup
- ✅ Database connections
- ✅ Authentication system
- ✅ Base test utilities

## Test Utilities

The `BaseTestCase` class in `test_core.py` provides common utilities:

- `create_user()` - Helper to create test users
- `create_superuser()` - Helper to create test superusers
- Common test data setup

## Best Practices

1. **Isolation**: Each test is independent and doesn't rely on others
2. **Clean State**: Database is reset between tests
3. **Comprehensive Coverage**: Both happy path and edge cases are tested
4. **Clear Naming**: Test names clearly describe what they're testing
5. **Documentation**: Each test has docstrings explaining its purpose

## Adding New Tests

When adding new functionality to the project:

1. Add tests to the appropriate existing file, or
2. Create a new test file following the naming convention `test_<object_name>.py`
3. Inherit from `BaseTestCase` for common utilities
4. Follow the existing patterns for consistency

## Common Issues

- **Import Errors**: Make sure Django is properly configured before running tests
- **Database Errors**: Tests use a separate test database that's created/destroyed automatically
- **Permission Errors**: Some tests require authentication - use the provided helper methods