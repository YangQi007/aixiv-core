#!/bin/bash

# AIXIV Test Runner Script

echo "🧪 AIXIV Test Suite"
echo "===================="

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "❌ pytest not found. Installing..."
    pip install pytest pytest-cov
fi

# Default test options
TEST_OPTIONS=""
COVERAGE=false
VERBOSE=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -c|--coverage)
            COVERAGE=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            TEST_OPTIONS="$TEST_OPTIONS -v"
            shift
            ;;
        -k|--keyword)
            TEST_OPTIONS="$TEST_OPTIONS -k $2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -c, --coverage    Run tests with coverage report"
            echo "  -v, --verbose     Verbose output"
            echo "  -k, --keyword     Run tests matching keyword"
            echo "  -h, --help        Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                 # Run all tests"
            echo "  $0 -v              # Run tests with verbose output"
            echo "  $0 -c              # Run tests with coverage"
            echo "  $0 -k health       # Run tests containing 'health'"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Set up coverage if requested
if [ "$COVERAGE" = true ]; then
    TEST_OPTIONS="$TEST_OPTIONS --cov=app --cov-report=term-missing --cov-report=html"
    echo "📊 Coverage reporting enabled"
fi

# Run tests
echo "🚀 Running tests..."
echo "Command: pytest tests/ $TEST_OPTIONS"
echo ""

pytest tests/ $TEST_OPTIONS

# Show results
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ All tests passed!"
    if [ "$COVERAGE" = true ]; then
        echo "📊 Coverage report generated in htmlcov/"
        echo "💡 Open htmlcov/index.html in your browser to view coverage"
    fi
else
    echo ""
    echo "❌ Some tests failed!"
    exit 1
fi 