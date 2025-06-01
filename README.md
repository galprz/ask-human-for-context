# Ask Human for Context MCP Server

> **Bridge the gap between AI and human intelligence** - A Model Context Protocol (MCP) server that enables AI assistants to ask humans for missing context during conversations and development workflows.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)

## 🤖 What is this?

The **Ask Human for Context MCP Server** is a specialized tool that allows AI assistants (like Claude in Cursor) to pause their workflow and **ask you directly** for clarification, preferences, or missing information through native GUI dialogs.

### The Problem It Solves

When AI assistants encounter situations where they need human input to proceed effectively, they typically either:

- Make assumptions that might be wrong
- Ask generic questions in the chat
- Get stuck without clear direction

This MCP server enables **true human-in-the-loop workflows** where the AI can:

- ✅ Pause and ask for specific clarification
- ✅ Present context about why information is needed
- ✅ Get immediate, focused responses through native dialogs
- ✅ Continue with confidence based on your input

## 🎯 Use Cases

Perfect for scenarios where AI needs human guidance:

- **Multiple Implementation Approaches**: "Should I use React or Vue for this component?"
- **Technology Preferences**: "Which database would you prefer: PostgreSQL or MongoDB?"
- **Domain-Specific Requirements**: "What's the maximum file size for uploads in your system?"
- **User Experience Decisions**: "How should we handle errors - modal dialogs or inline messages?"
- **Code Architecture**: "Should this be a microservice or part of the monolith?"
- **Missing Context**: "What's the expected behavior when the API is down?"

## 🚀 Quick Start with Cursor

### 1. Add to Cursor MCP Configuration

Add this to your Cursor MCP settings (`~/.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "ask-human-for-context": {
      "command": "uvx",
      "args": ["ask-human-for-context-mcp", "--transport", "stdio"]
    }
  }
}
```

> **Note**: No manual installation needed! uvx automatically downloads and runs the package from PyPI.

### 2. Restart Cursor

The MCP server will now be available to Claude in your Cursor sessions!

## 💬 How It Works

### For AI Assistants

When Claude (or another AI) needs human input, it can call the `asking_user_missing_context` tool:

```python
# AI calls this tool when it needs clarification
asking_user_missing_context(
    question="Should I implement authentication using JWT tokens or session cookies?",
    context="I'm building the login system for your web app. Both approaches are valid, but they have different security and performance trade-offs."
)
```

### For Humans

You'll see a native dialog box like this:

```
📋 Missing Context:
I'm building the login system for your web app. Both approaches are
valid, but they have different security and performance trade-offs.

────────────────────────────────────────

❓ Question:
Should I implement authentication using JWT tokens or session cookies?

[Text Input Field]
[    OK    ] [  Cancel  ]
```

Your response gets sent back to the AI to continue the workflow.

## 🖥️ Platform Support

### Cross-Platform Native Dialogs

| Platform    | Technology  | Features                              |
| ----------- | ----------- | ------------------------------------- |
| **macOS**   | `osascript` | Custom Cursor icon, 90-second timeout |
| **Linux**   | `zenity`    | Custom window icon, proper styling    |
| **Windows** | `tkinter`   | Native Windows dialogs                |

### Automatic Fallbacks

- Graceful error handling if GUI systems aren't available
- Clear error messages with troubleshooting guidance
- No crashes or hanging - always responds to the AI

## 🔧 Installation Options

### Option 1: uvx (Recommended - Production Ready)

Simply add to your Cursor MCP configuration - no manual installation required:

```json
{
  "ask-human-for-context": {
    "command": "uvx",
    "args": ["ask-human-for-context-mcp", "--transport", "stdio"]
  }
}
```

> **✨ Auto-Install**: uvx automatically downloads the latest version from PyPI!  
> **🔄 Auto-Update**: uvx handles version management and updates seamlessly.

### Option 2: pip + Virtual Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install package
pip install ask-human-for-context-mcp

# Add to Cursor config
{
  "ask-human-for-context": {
    "command": "/path/to/venv/bin/ask-human-for-context-mcp",
    "args": ["--transport", "stdio"]
  }
}
```

### Option 3: Development Installation

```bash
# Clone and install for development
git clone https://github.com/galperetz/ask-human-for-context-mcp.git
cd ask-human-for-context-mcp
pip install -e .

# Use in Cursor config (local development)
{
  "ask-human-for-context": {
    "command": "uvx",
    "args": ["--from", "/path/to/project", "ask-human-for-context-mcp", "--transport", "stdio"]
  }
}
```

> **Note**: For production use, prefer Option 1 which uses the published PyPI package.

## ⚙️ Configuration

### Transport Modes

#### STDIO (Default)

Perfect for MCP clients like Cursor:

```bash
ask-human-for-context-mcp --transport stdio
```

#### SSE (Server-Sent Events)

For web applications:

```bash
ask-human-for-context-mcp --transport sse --host 0.0.0.0 --port 8080
```

### Timeout Settings

- **Default timeout**: 90 seconds (1.5 minutes)
- **Configurable range**: 30 seconds to 2 hours
- **User-friendly**: Shows timeout in minutes for better UX

## 🔍 Tool Reference

### `asking_user_missing_context`

Ask the user for missing context during AI workflows.

**Parameters:**

- `question` (string, required): The specific question (max 1000 chars)
- `context` (string, optional): Background explaining why context is needed (max 2000 chars)

**Returns:**

- `✅ User response: [user's answer]` - When user provides input
- `⚠️ Empty response received` - When user clicks OK without entering text
- `⚠️ Timeout: No response within [time]` - When dialog times out
- `⚠️ Cancelled: User cancelled the prompt` - When user cancels dialog
- `❌ Error: [description]` - When there are validation or system errors

**Example Usage:**

```python
# Simple question
result = asking_user_missing_context(
    question="What's the preferred color scheme for the UI?"
)

# Question with context
result = asking_user_missing_context(
    question="Should I use REST or GraphQL for the API?",
    context="I'm designing the backend architecture. The frontend will need to fetch user data, posts, and comments. Performance and caching are important considerations."
)
```

## 🛠️ Development

### Requirements

- Python 3.8+
- Dependencies: `mcp`
- Platform-specific: `osascript` (macOS), `zenity` (Linux), `tkinter` (Windows)

### Building

```bash
# Install dependencies
pip install -e .

# Build package
uv build

# Run tests
pytest
```

### Project Structure

```
ask-human-for-context-mcp/
├── src/ask_human_for_context_mcp/
│   ├── __init__.py
│   ├── __main__.py
│   └── server.py           # Main MCP server implementation
├── assets/
│   └── cursor-icon.icns    # Custom Cursor icon for dialogs
├── pyproject.toml          # Project configuration
└── README.md
```

## 🤝 Integration Examples

### Cursor AI Development Workflow

1. **AI encounters decision point**: "I need to choose between TypeScript and JavaScript"
2. **AI calls the tool**: Provides context about the project and asks for preference
3. **User sees dialog**: Native popup with formatted question and context
4. **User responds**: Types preference and clicks OK
5. **AI continues**: Uses the human input to make informed decisions

### Perfect for:

- **Code reviews**: "Should I refactor this function or leave it as-is?"
- **Architecture decisions**: "Microservices or monolith for this feature?"
- **UI/UX choices**: "Modal dialog or inline editing for this form?"
- **Technology selection**: "Which CSS framework fits your preferences?"

## 🔒 Security & Privacy

- **Local execution**: All dialogs run locally on your machine
- **No data collection**: No user responses are logged or transmitted
- **Secure communication**: Uses MCP's secure transport protocols
- **Timeout protection**: Automatic cleanup prevents hanging processes

## 📜 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/galperetz/ask-human-for-context-mcp/issues)
- **Documentation**: [Model Context Protocol](https://modelcontextprotocol.io/)
- **MCP Community**: [MCP Discussions](https://github.com/modelcontextprotocol/specification/discussions)

---

**Made with ❤️ for better human-AI collaboration**
