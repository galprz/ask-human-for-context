"""Test entry points and command line functionality."""
import pytest
import subprocess
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

def test_main_module_execution():
    """Test that the package can be run as a module."""
    result = subprocess.run([sys.executable, "-m", "ask_human_for_context_mcp", "--help"], capture_output=True, text=True, cwd=os.path.join(os.path.dirname(__file__), ".."))
    assert result.returncode == 0
    assert "transport" in result.stdout

def test_installed_command():
    """Test that the installed command works."""
    try:
        result = subprocess.run(["ask-human-for-context-mcp", "--help"], capture_output=True, text=True)
        assert result.returncode == 0
        assert "transport" in result.stdout
    except FileNotFoundError:
        pytest.skip("ask-human-for-context-mcp command not installed")
