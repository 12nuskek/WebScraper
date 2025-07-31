#!/usr/bin/env python
"""
Test runner script for WebScraper project.

This script sets up the Django environment and runs all tests in the tests/ directory.
Run this from the project root directory.

Usage:
    python tests/run_tests.py                    # Run all tests
    python tests/run_tests.py test_user_model    # Run specific test file
    python tests/run_tests.py -v 2               # Run with verbose output
"""

import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner


def setup_django():
    """Set up Django environment for running tests."""
    # Add the project root to the Python path
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    scraping_backend_path = os.path.join(project_root, 'scraping-backend')
    
    if scraping_backend_path not in sys.path:
        sys.path.insert(0, scraping_backend_path)
    
    # Set the Django settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
    
    # Setup Django
    django.setup()


def run_tests(test_labels=None, verbosity=1):
    """Run the tests using Django's test runner."""
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=verbosity, interactive=True)
    
    if not test_labels:
        # Run all tests in the tests package
        test_labels = ['tests']
    
    failures = test_runner.run_tests(test_labels)
    return failures


if __name__ == '__main__':
    setup_django()
    
    # Parse command line arguments
    test_labels = []
    verbosity = 1
    
    for arg in sys.argv[1:]:
        if arg == '-v':
            continue
        elif arg.isdigit() and sys.argv[sys.argv.index(arg) - 1] == '-v':
            verbosity = int(arg)
        else:
            test_labels.append(f'tests.{arg}' if not arg.startswith('tests.') else arg)
    
    # Run tests
    failures = run_tests(test_labels, verbosity)
    
    if failures:
        print(f"\n{failures} test(s) failed.")
        sys.exit(1)
    else:
        print("\nAll tests passed!")
        sys.exit(0)