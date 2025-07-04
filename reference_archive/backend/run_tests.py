#!/usr/bin/env python3
"""
Comprehensive test runner for the Tariff AI Backend
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def run_tests():
    """Run all backend tests with coverage and reporting."""
    import pytest
    
    # Test configuration
    test_args = [
        "tests/",
        "-v",  # Verbose output
        "--tb=short",  # Short traceback format
        "--strict-markers",
        "--disable-warnings",
        "--cov=app",  # Coverage for app module
        "--cov-report=term-missing",  # Show missing lines in terminal
        "--cov-report=html:htmlcov",  # Generate HTML coverage report
        "--cov-report=xml",  # Generate XML coverage report for CI
        "--cov-fail-under=80",  # Fail if coverage is below 80%
        "--durations=10",  # Show 10 slowest tests
        "--maxfail=5",  # Stop after 5 failures
    ]
    
    print("🚀 Starting Tariff AI Backend Tests")
    print("=" * 50)
    
    # Run the tests
    exit_code = pytest.main(test_args)
    
    if exit_code == 0:
        print("\n✅ All tests passed!")
        print("📊 Coverage reports generated:")
        print("   - HTML: htmlcov/index.html")
        print("   - XML: coverage.xml")
    else:
        print(f"\n❌ Tests failed with exit code: {exit_code}")
    
    return exit_code

def run_unit_tests():
    """Run only unit tests."""
    import pytest
    
    test_args = [
        "tests/",
        "-v",
        "-m", "unit",
        "--tb=short",
        "--disable-warnings",
    ]
    
    print("🧪 Running Unit Tests")
    print("=" * 30)
    
    exit_code = pytest.main(test_args)
    return exit_code

def run_api_tests():
    """Run only API tests."""
    import pytest
    
    test_args = [
        "tests/",
        "-v",
        "-m", "api",
        "--tb=short",
        "--disable-warnings",
    ]
    
    print("🌐 Running API Tests")
    print("=" * 30)
    
    exit_code = pytest.main(test_args)
    return exit_code

def run_integration_tests():
    """Run only integration tests."""
    import pytest
    
    test_args = [
        "tests/",
        "-v",
        "-m", "integration",
        "--tb=short",
        "--disable-warnings",
    ]
    
    print("🔗 Running Integration Tests")
    print("=" * 30)
    
    exit_code = pytest.main(test_args)
    return exit_code

def run_slow_tests():
    """Run only slow tests."""
    import pytest
    
    test_args = [
        "tests/",
        "-v",
        "-m", "slow",
        "--tb=short",
        "--disable-warnings",
    ]
    
    print("🐌 Running Slow Tests")
    print("=" * 30)
    
    exit_code = pytest.main(test_args)
    return exit_code

def run_e2e_tests():
    """Run only end-to-end tests."""
    import pytest
    
    test_args = [
        "tests/",
        "-v",
        "-m", "e2e",
        "--tb=short",
        "--disable-warnings",
    ]
    
    print("🔍 Running End-to-End Tests")
    print("=" * 30)
    
    exit_code = pytest.main(test_args)
    return exit_code

def check_test_environment():
    """Check if the test environment is properly set up."""
    print("🔧 Checking Test Environment")
    print("=" * 30)
    
    # Check if required packages are installed
    required_packages = [
        "pytest",
        "pytest-asyncio",
        "pytest-cov",
        "httpx",
        "fastapi",
        "sqlalchemy",
        "chromadb"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Install with: pip install " + " ".join(missing_packages))
        return False
    
    # Check if test database can be created
    try:
        from app.db.base import Base
        from sqlalchemy.ext.asyncio import create_async_engine
        import aiosqlite
        
        print("✅ Database dependencies")
    except ImportError as e:
        print(f"❌ Database dependencies - {e}")
        return False
    
    # Check if test data files exist
    test_files = [
        "tariff_database_2025.xlsx",
        "adcvd_faq.json"
    ]
    
    for file in test_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"⚠️  {file} - Not found (optional)")
    
    print("\n✅ Test environment check completed")
    return True

def main():
    """Main test runner function."""
    if len(sys.argv) < 2:
        print("Usage: python run_tests.py [command]")
        print("\nCommands:")
        print("  all          - Run all tests with coverage")
        print("  unit         - Run only unit tests")
        print("  api          - Run only API tests")
        print("  integration  - Run only integration tests")
        print("  slow         - Run only slow tests")
        print("  e2e          - Run only end-to-end tests")
        print("  check        - Check test environment")
        print("  help         - Show this help message")
        return 1
    
    command = sys.argv[1].lower()
    
    if command == "all":
        return run_tests()
    elif command == "unit":
        return run_unit_tests()
    elif command == "api":
        return run_api_tests()
    elif command == "integration":
        return run_integration_tests()
    elif command == "slow":
        return run_slow_tests()
    elif command == "e2e":
        return run_e2e_tests()
    elif command == "check":
        success = check_test_environment()
        return 0 if success else 1
    elif command == "help":
        print("Tariff AI Backend Test Runner")
        print("=" * 30)
        print("This script runs various types of tests for the Tariff AI backend.")
        print("\nAvailable commands:")
        print("  all          - Run all tests with coverage reporting")
        print("  unit         - Run only unit tests (fast)")
        print("  api          - Run only API endpoint tests")
        print("  integration  - Run only integration tests")
        print("  slow         - Run only slow tests")
        print("  e2e          - Run only end-to-end tests")
        print("  check        - Check if test environment is properly set up")
        print("  help         - Show this help message")
        print("\nExamples:")
        print("  python run_tests.py all")
        print("  python run_tests.py unit")
        print("  python run_tests.py api")
        return 0
    else:
        print(f"Unknown command: {command}")
        print("Use 'python run_tests.py help' for usage information")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 