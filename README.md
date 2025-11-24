# Clockify MCP Server

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server for seamless integration with Clockify time tracking.

## Features

- **Start Timer**: Create new time entries with descriptions and project associations.
- **Get Active Timer**: View the currently running timer and its duration.
- **Stop Timer**: Stop the active timer and receive a summary of the entry.

## Requirements

- **Docker**: Must be installed and running.
- **Clockify Account**: You need an active account.
- **Clockify API Key**: Generated from your profile settings.
- **Workspace ID**: The ID of the workspace you want to track time in.

## Setup

### 1. Get Credentials

1.  **API Key**:
    *   Log in to [Clockify](https://clockify.me).
    *   Go to **Profile Settings**.
    *   Scroll to the **API** section and generate/copy your API key.

2.  **Workspace ID**:
    *   Navigate to **Settings** > **Workspace** in Clockify.
    *   Copy the ID from the URL: `https://app.clockify.me/workspaces/{WORKSPACE_ID}/settings`.

### 2. Build Docker Image

Navigate to the project directory and build the image:

```bash
docker build -t clockify-mcp-server .
```

### 3. Configure Claude Desktop

Add the server configuration to your `claude_desktop_config.json`:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "clockify": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e",
        "CLOCKIFY_API_KEY=your_api_key_here",
        "-e",
        "CLOCKIFY_WORKSPACE_ID=your_workspace_id_here",
        "clockify-mcp-server"
      ]
    }
  }
}
```

> [!IMPORTANT]
> Replace `your_api_key_here` and `your_workspace_id_here` with your actual credentials.

### 4. Restart Claude

Quit and restart Claude Desktop to load the new server.

## Usage

You can interact with the Clockify MCP server using natural language in Claude.

### Available Tools

| Tool | Description | Parameters |
| :--- | :--- | :--- |
| `start_timer` | Starts a new timer. | `description` (required), `project_name` (required), `task_id` (optional), `tags` (optional) |
| `get_active_timer` | Shows the running timer. | None |
| `stop_timer` | Stops the current timer. | None |

### Examples

**Start a timer:**
> "Start a timer for 'Writing documentation' on project 'DevOps'"
> "Begin tracking time on 'Bug Fixes' for project 'Mobile App'"

**Check status:**
> "What am I working on right now?"
> "Show my active timer"

**Stop a timer:**
> "Stop my current timer"
> "I'm done with this task"

## Troubleshooting

| Problem | Solution |
| :--- | :--- |
| **Missing Environment Variables** | Ensure `CLOCKIFY_API_KEY` and `CLOCKIFY_WORKSPACE_ID` are set in the config file. |
| **Project Not Found** | Verify the project exists in Clockify and the name matches exactly (case-insensitive). |
| **No Active Timer** | You must start a timer with `start_timer` before you can stop one. |
| **Server Fails to Start** | Check Docker logs: `docker logs <container_id>`. |

## Security

- **API Keys**: Passed securely as environment variables; never hardcoded.
- **Container**: Runs as a non-root user for added security.
- **Communication**: All API requests use HTTPS.
- **Data**: No sensitive data is stored locally.

## Support

- **Clockify API**: [https://docs.clockify.me/](https://docs.clockify.me/)
- **MCP Documentation**: [https://modelcontextprotocol.io/](https://modelcontextprotocol.io/)
