"""Test configuration for pytest."""
import os
import sys

# Add src directory to Python path for testing
test_dir = os.path.dirname(__file__)
src_dir = os.path.join(test_dir, "..", "src")
sys.path.insert(0, os.path.abspath(src_dir))
