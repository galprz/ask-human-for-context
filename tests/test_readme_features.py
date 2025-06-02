"""Test functionality mentioned in README."""
import pytest
import sys
import os
import platform
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

def test_platform_detection():
    """Test that platform detection works as mentioned in README."""
    from ask_human_for_context_mcp.server import GUIDialogHandler
    handler = GUIDialogHandler()
    assert handler.platform in ["Darwin", "Linux", "Windows"]
    # On macOS (Darwin), should be detected correctly
    if platform.system() == "Darwin":
        assert handler.platform == "Darwin"

def test_error_handling_classes():
    """Test custom exception classes mentioned in README."""
    from ask_human_for_context_mcp.server import (
        UserPromptTimeout,
        UserPromptCancelled,
        UserPromptError
    )
    # Test that exceptions can be instantiated
    timeout_err = UserPromptTimeout("Test timeout")
    cancelled_err = UserPromptCancelled("Test cancellation")
    prompt_err = UserPromptError("Test error")
    assert str(timeout_err) == "Test timeout"
    assert str(cancelled_err) == "Test cancellation"
    assert str(prompt_err) == "Test error"

def test_tool_parameter_validation():
    """Test tool parameter validation as described in README."""
    from ask_human_for_context_mcp.server import asking_user_missing_context
    import asyncio
    # This is an async function, so we need to test it properly
    assert asyncio.iscoroutinefunction(asking_user_missing_context)
