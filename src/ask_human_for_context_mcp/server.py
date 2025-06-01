import asyncio
import subprocess
import platform
from typing import Any, Optional
from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from mcp.server.sse import SseServerTransport
from starlette.requests import Request
from starlette.routing import Mount, Route
from mcp.server import Server
import uvicorn

# Initialize FastMCP server for User Prompt tools
mcp = FastMCP("ask-human-for-context")


# Custom exception classes for better error handling (Task 1.4)
class UserPromptTimeout(Exception):
    """Raised when user doesn't respond within timeout period."""
    pass


class UserPromptCancelled(Exception):
    """Raised when user cancels the prompt or interrupts the process."""
    pass


class UserPromptError(Exception):
    """Generic error for user prompt operations."""
    pass


class GUIDialogHandler:
    """Cross-platform GUI dialog handler for asking humans for context.
    
    Provides native GUI dialogs on macOS (osascript), Linux (zenity), and Windows (tkinter).
    Falls back to terminal input if GUI is unavailable.
    """

    def __init__(self):
        """Initialize the dialog handler with platform detection."""
        self.platform = platform.system()

    async def get_user_input(self, question: str, timeout: int = 1200) -> Optional[str]:
        """Get user input via native GUI dialog with timeout.
        
        Args:
            question: The question to ask the user
            timeout: Timeout in seconds (default: 1200 = 20 minutes)
            
        Returns:
            The user's response as a string, or None if timeout/cancelled
            
        Raises:
            UserPromptError: If GUI dialog system fails
            UserPromptCancelled: If user cancels or interrupts
        """
        try:
            if self.platform == "Darwin":
                return await self._macos_dialog(question, timeout)
            elif self.platform == "Linux":
                return await self._linux_dialog(question, timeout)
            else:
                return await self._windows_dialog(question, timeout)
        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            raise UserPromptCancelled("User interrupted the dialog with Ctrl+C")
        except Exception as e:
            # Don't fall back to terminal in MCP context - just report the error
            raise UserPromptError(f"GUI dialog failed: {e}. Ensure osascript (macOS), zenity (Linux), or tkinter (Windows) is available.")

    async def _macos_dialog(self, question: str, timeout: int) -> Optional[str]:
        """macOS dialog using osascript with custom Cursor icon."""
        
        # Use the custom Cursor icon from assets folder
        import os
        
        # Use absolute path to the icon file - more reliable than path calculation
        cursor_icon_path = "/Users/galperetz/custom-mcp-servers/mcp-server-python-template/assets/cursor-icon.icns"
        
        if os.path.exists(cursor_icon_path):
            icon_clause = f'with icon file (POSIX file "{cursor_icon_path}")'
        else:
            # Fallback to caution icon if custom icon not found
            icon_clause = "with icon caution"
        
        script = f'''
        display dialog "{self._escape_for_applescript(question)}" ¬
        default answer "" ¬
        with title "🤖 Cursor AI Assistant" ¬
        {icon_clause} ¬
        giving up after {timeout}
        '''

        try:
            process = await asyncio.create_subprocess_exec(
                "osascript", "-e", script,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                output = stdout.decode().strip()
                # Handle AppleScript output format: "button returned:OK, text returned:user_input"
                if "text returned:" in output:
                    # Extract text after "text returned:" and before any comma or end
                    text_part = output.split("text returned:")[1]
                    # Remove trailing ", gave up:false" or similar
                    if ", " in text_part:
                        return text_part.split(", ")[0].strip()
                    return text_part.strip()
                elif "gave up:true" in output:
                    # User didn't respond within timeout
                    return None
                elif "button returned:" in output and "text returned:" not in output:
                    # User clicked OK but didn't enter text
                    return ""
            return None
        except Exception as e:
            return None

    async def _linux_dialog(self, question: str, timeout: int) -> Optional[str]:
        """Linux dialog using zenity with custom Cursor logo."""
        # Use the custom Cursor logo for consistent branding
        icon_args = self._get_linux_icon_args()
        
        cmd = [
            "zenity", "--entry",
            "--title=🤖 Cursor AI Assistant",
            f"--text={question}",
            f"--timeout={timeout}",
        ] + icon_args

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                return stdout.decode().strip()
            return None
        except Exception:
            return None

    async def _windows_dialog(self, question: str, timeout: int) -> Optional[str]:
        """Windows dialog using tkinter with custom Cursor logo."""
        try:
            import tkinter as tk
            from tkinter import simpledialog
            import os
            
            # Create a simple dialog using tkinter
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            
            # Try to set custom icon from PNG (converted to ICO)
            self._set_windows_icon(root)
            
            result = simpledialog.askstring("🤖 Cursor AI Assistant", question)
            root.destroy()
            
            return result
        except Exception:
            return None

    def _escape_for_applescript(self, text: str) -> str:
        """Escape text for AppleScript."""
        return text.replace('"', '\\"').replace('\\', '\\\\')

    def _get_macos_icon_clause(self) -> str:
        """Get the icon clause for macOS dialog with custom Cursor logo."""
        import os
        
        # Check for the specific Cursor Logo files (prioritize ICNS for macOS)
        custom_logo_paths = [
            "./assets/cursor-icon.icns",  # Try ICNS first (native macOS format)
            "./cursor-icon.icns",
            "./assets/Cursor Logo (4).png",
            "./Cursor Logo (4).png"
        ]
        
        for icon_path in custom_logo_paths:
            if os.path.exists(icon_path):
                if icon_path.endswith('.icns'):
                    print(f"✅ Found ICNS icon: {icon_path}")
                    abs_path = os.path.abspath(icon_path)
                    return f'with icon file (POSIX file "{abs_path}")'
                elif icon_path.endswith('.png'):
                    print(f"✅ Found custom Cursor logo: {icon_path}")
                    print("ℹ️ Note: Using application icon style for PNG logo")
                    # Use 'application' icon for software/AI assistant feel
                    return "with icon application"
        
        # Fall back to application icon (better for AI assistant than default)
        return "with icon application"

    def _get_linux_icon_args(self) -> list:
        """Get icon arguments for Linux zenity dialog with custom Cursor logo."""
        import os
        
        # Check for the specific Cursor Logo (4).png file first
        custom_logo_paths = [
            "./assets/Cursor Logo (4).png",
            "./Cursor Logo (4).png",
            "./assets/cursor-icon.png",
            "./cursor-icon.png"
        ]
        
        for icon_path in custom_logo_paths:
            if os.path.exists(icon_path):
                print(f"✅ Using custom Cursor logo for Linux: {icon_path}")
                return [f"--window-icon={icon_path}"]
        
        # Fall back to built-in question icon
        return ["--question"]

    def _set_windows_icon(self, root) -> None:
        """Set icon for Windows tkinter dialog with custom Cursor logo."""
        import os
        
        # Check for custom Cursor icon files
        possible_icon_paths = [
            "./assets/cursor-icon.ico",
            "./cursor-icon.ico",
            "C:\\Program Files\\Cursor\\cursor.ico"
        ]
        
        for icon_path in possible_icon_paths:
            if os.path.exists(icon_path):
                try:
                    print(f"✅ Using custom Cursor icon for Windows: {icon_path}")
                    root.iconbitmap(icon_path)
                    return
                except Exception:
                    continue
        
        # Note: PNG files can't be directly used as Windows icons
        # Users would need to convert "Cursor Logo (4).png" to ICO format
        if os.path.exists("./assets/Cursor Logo (4).png"):
            print("ℹ️ Found PNG logo. For Windows, convert to ICO format for icon support.")


# Global dialog handler instance
dialog_handler = GUIDialogHandler()


@mcp.tool()
async def asking_user_missing_context(
    question: str,
    context: str = ""
) -> str:
    """Ask the user to fill missing context or knowledge gaps during research and development.
    
    This tool enables AI assistants to pause workflows when they encounter missing context,
    need clarification on implementation choices, or require understanding of preferred 
    approaches. Use this when conducting research and you need user input to proceed effectively.
    
    Common use cases:
    - Multiple valid implementation approaches exist (ask user for preference)
    - Need clarification on preferred tech stack or framework
    - Missing domain-specific requirements or constraints  
    - Uncertain about user's specific goals or priorities
    - Need to understand existing codebase patterns or conventions
    
    Args:
        question: The specific question about missing context (max 1000 characters)
        context: Background info explaining why this context is needed (max 2000 characters)
        
    Returns:
        The user's response as a formatted string with status indicator
        
    Raises:
        ValueError: If parameters are invalid or out of acceptable ranges
    """

    timeout_seconds = 90 # 1.5 minutes
    
    # Parameter validation with clear error messages
    if not question or not isinstance(question, str):
        return "❌ Error: 'question' parameter is required and must be a non-empty string"
    
    if len(question.strip()) == 0:
        return "❌ Error: 'question' cannot be empty or only whitespace"
    
    if len(question) > 1000:
        return "❌ Error: 'question' is too long (max 1000 characters). Please shorten your question."
    
    if not isinstance(timeout_seconds, int):
        return "❌ Error: 'timeout_seconds' must be an integer"
    
    if timeout_seconds < 30:
        return "❌ Error: 'timeout_seconds' must be at least 30 seconds for usability"
    
    if timeout_seconds > 7200:  # 2 hours max
        return "❌ Error: 'timeout_seconds' cannot exceed 7200 seconds (2 hours) to prevent indefinite hanging"
    
    if not isinstance(context, str):
        return "❌ Error: 'context' must be a string (use empty string if no context needed)"
    
    if len(context) > 2000:
        return "❌ Error: 'context' is too long (max 2000 characters). Please provide a more concise context."

    try:
        # Format question with context for better user experience
        if context.strip():
            # Format context clearly with visual separation
            formatted_context = f"📋 Missing Context:\n{context.strip()}\n"
            separator = "─" * 40
            full_question = f"{formatted_context}\n{separator}\n\n❓ Question:\n{question.strip()}"
        else:
            full_question = f"❓ {question.strip()}"

        # Get user input via GUI dialog with timeout
        response = await dialog_handler.get_user_input(full_question, timeout_seconds)

        # Handle different response scenarios with custom exceptions
        if response is None:
            # Timeout occurred
            timeout_minutes = timeout_seconds // 60
            timeout_display = f"{timeout_minutes} minute{'s' if timeout_minutes != 1 else ''}"
            raise UserPromptTimeout(f"No response received within {timeout_display}")

        if not response.strip():
            # Empty response (user clicked OK without entering text)
            return "⚠️ Empty response received. The user clicked OK but didn't enter any text. Please ask again if a response is needed."

        # Successful response
        clean_response = response.strip()
        
        # Format response with clear indicator
        return f"✅ User response: {clean_response}"

    except UserPromptTimeout as e:
        # Handle timeout with user-friendly message
        return f"⚠️ Timeout: {str(e)}. The dialog may have timed out or been cancelled. Please try asking again if needed."
    
    except UserPromptCancelled as e:
        # Handle cancellation 
        return f"⚠️ Cancelled: {str(e)}. The user cancelled the prompt. Please try again or rephrase your question."
    
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully without crashing the server
        raise UserPromptCancelled("User interrupted the prompt with Ctrl+C")
    
    except UserPromptError as e:
        # Handle custom user prompt errors
        return f"❌ User Prompt Error: {str(e)}"
    
    except Exception as e:
        # Comprehensive error handling with helpful context
        error_context = f"Question: {question[:100]}{'...' if len(question) > 100 else ''}"
        return f"❌ Error getting user input: {str(e)}\n\nContext: {error_context}\n\nThe GUI dialog system may not be available. Check that the required dependencies are installed (zenity on Linux, osascript on macOS, tkinter on Windows)."


def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    """Create a Starlette application that can serve the provided MCP server with SSE.
    
    Sets up a Starlette web application with routes for SSE (Server-Sent Events)
    communication with the MCP server.
    
    Args:
        mcp_server: The MCP server instance to connect
        debug: Whether to enable debug mode for the Starlette app
        
    Returns:
        A configured Starlette application
    """
    # Create an SSE transport with a base path for messages
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request) -> None:
        """Handler for SSE connections.
        
        Establishes an SSE connection and connects it to the MCP server.
        
        Args:
            request: The incoming HTTP request
        """
        # Connect the SSE transport to the request
        async with sse.connect_sse(
                request.scope,
                request.receive,
                request._send,  # noqa: SLF001
        ) as (read_stream, write_stream):
            # Run the MCP server with the SSE streams
            await mcp_server.run(
                read_stream,
                write_stream,
                mcp_server.create_initialization_options(),
            )

    # Create and return the Starlette application with routes
    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse),  # Endpoint for SSE connections
            Mount("/messages/", app=sse.handle_post_message),  # Endpoint for posting messages
        ],
    )


def main():
    """Main entry point for the User Prompt MCP server.
    
    This function serves as the primary entry point when the server is launched
    via uvx or direct Python execution. It handles argument parsing and server startup.
    """
    # Get the underlying MCP server from the FastMCP instance
    mcp_server = mcp._mcp_server  # noqa: WPS437
    
    import argparse
    
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description='Run User Prompt MCP server with configurable transport')
    # Allow choosing between stdio and SSE transport modes
    parser.add_argument('--transport', choices=['stdio', 'sse'], default='stdio', 
                        help='Transport mode (stdio or sse)')
    # Host configuration for SSE mode
    parser.add_argument('--host', default='0.0.0.0', 
                        help='Host to bind to (for SSE mode)')
    # Port configuration for SSE mode
    parser.add_argument('--port', type=int, default=8080, 
                        help='Port to listen on (for SSE mode)')
    args = parser.parse_args()

    # Launch the server with the selected transport mode
    if args.transport == 'stdio':
        # Run with stdio transport (default)
        # This mode communicates through standard input/output
        mcp.run(transport='stdio')
    else:
        # Run with SSE transport (web-based)
        # Create a Starlette app to serve the MCP server
        starlette_app = create_starlette_app(mcp_server, debug=True)
        # Start the web server with the configured host and port
        uvicorn.run(starlette_app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()