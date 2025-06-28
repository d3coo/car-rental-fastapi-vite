# MCP (Model Context Protocol) Setup Guide

This project is configured with MCP servers to enhance Claude Code's capabilities for Firebase development, file management, and Git operations.

## Prerequisites

1. **Node.js and npm** - Required for running MCP servers
2. **Firebase CLI Authentication** - Required for Firebase MCP server

## Setup Instructions

### 1. Authenticate Firebase CLI

Before using the Firebase MCP server, authenticate with Firebase:

```bash
npx -y firebase-tools@latest login --reauth
```

This will open a browser window for Firebase authentication.

### 2. Verify MCP Configuration

The project includes a `.mcp.json` file with the following configured servers:

- **Firebase** - Manage Firebase projects, Firestore, Authentication, etc.
- **Filesystem** - Read and write project files
- **Git** - Version control operations

### 3. Load MCP Configuration in Claude Code

The MCP configuration is automatically loaded when you use Claude Code in this project directory.

You can verify the MCP servers are loaded by running:
```bash
/mcp
```

## Available MCP Servers

### Firebase MCP Server
- **Purpose**: Interact with Firebase services
- **Capabilities**:
  - Create and manage Firebase projects
  - Manage Authentication users
  - Work with Firestore databases
  - Retrieve database schemas
  - Understand security rules
  - Send Cloud Messaging
  - And 40+ other Firebase tools

### Filesystem MCP Server
- **Purpose**: File system operations
- **Capabilities**:
  - Read files and directories
  - Write and edit files
  - Create new files and folders
  - File system navigation

### Git MCP Server
- **Purpose**: Git version control operations
- **Capabilities**:
  - View git status and history
  - Manage branches
  - Commit changes
  - View diffs and logs

## Usage Examples

### Firebase Operations
With the Firebase MCP server, Claude Code can:
```bash
# List Firebase projects
firebase projects:list

# Get Firestore data
firebase firestore:get

# Manage authentication users
firebase auth:users
```

### File Operations
With the Filesystem MCP server, Claude Code can:
- Read configuration files
- Edit source code
- Create new components
- Analyze project structure

### Git Operations
With the Git MCP server, Claude Code can:
- Check repository status
- View commit history
- Manage branches
- Create commits

## Security Considerations

- The Filesystem server is restricted to the project directory: `/Users/deco/Documents/GitHub/Contract-Editor/new-structure`
- Git operations are limited to this repository
- Firebase operations require proper authentication and project permissions
- Always review MCP server actions before executing

## Troubleshooting

### Firebase Authentication Issues
If you encounter Firebase authentication issues:
```bash
# Re-authenticate
npx firebase logout
npx firebase login --reauth
```

### MCP Server Not Loading
If MCP servers don't load:
1. Ensure Node.js is installed
2. Check that the `.mcp.json` file is valid JSON
3. Verify you're in the correct project directory
4. Restart Claude Code

### Missing Dependencies
If you get "command not found" errors:
```bash
# Install missing packages globally
npm install -g firebase-tools
npm install -g @modelcontextprotocol/server-filesystem
npm install -g @modelcontextprotocol/server-git
```

## Configuration Customization

To add additional MCP servers, edit the `.mcp.json` file:

```json
{
  "mcpServers": {
    "new-server": {
      "command": "npx",
      "args": ["-y", "package-name"],
      "env": {
        "API_KEY": "your-api-key"
      },
      "description": "Description of the server"
    }
  }
}
```

## Documentation Links

- [Claude Code MCP Documentation](https://docs.anthropic.com/en/docs/claude-code/mcp)
- [Firebase MCP Server Documentation](https://firebase.google.com/docs/cli/mcp-server)
- [Model Context Protocol Specification](https://spec.modelcontextprotocol.io/)

## Project Integration

This MCP configuration is specifically designed for the Car Rental Management System project:

- **Firebase integration** for Firestore database operations
- **File system access** for code generation and editing
- **Git operations** for version control management

The configuration supports the project's tech stack:
- FastAPI backend with Domain-Driven Design
- Firebase Firestore database
- React frontend (Vite)
- pnpm monorepo structure