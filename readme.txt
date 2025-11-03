CLOCKIFY MCP SERVER
===================

A Model Context Protocol (MCP) server for Clockify time tracking integration.

FEATURES
--------
- Start timer: Create a new time entry with description and project
- Get active timer: View the currently running timer with duration
- Stop timer: Stop the active timer and get final details

REQUIREMENTS
------------
- Docker installed and running
- Clockify account with API access
- Clockify API key
- Clockify Workspace ID

SETUP INSTRUCTIONS
------------------

1. Get Your Clockify API Key
   - Log in to Clockify at https://clockify.me
   - Go to Profile Settings
   - Scroll down to "API" section
   - Copy your API key

2. Get Your Workspace ID
   - In Clockify, go to Settings > Workspace
   - Your workspace ID is in the URL: https://app.clockify.me/workspaces/{WORKSPACE_ID}/settings
   - Copy the workspace ID from the URL

3. Build the Docker Image
   Navigate to the clockify-mcp-server directory and run:
   
   cd clockify-mcp-server
   docker build -t clockify-mcp-server .

4. Configure Claude Desktop
   Edit your Claude Desktop configuration file:
   
   macOS: ~/Library/Application Support/Claude/claude_desktop_config.json
   Windows: %APPDATA%\Claude\claude_desktop_config.json
   
   Add this configuration:
   
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
   
   Replace 'your_api_key_here' with your actual Clockify API key
   Replace 'your_workspace_id_here' with your actual Workspace ID

5. Restart Claude Desktop
   Quit and restart Claude Desktop to load the new server

AVAILABLE TOOLS
---------------

1. start_timer
   - Description: Start a new Clockify timer
   - Required Parameters:
     * description: What you're working on
     * project_name: Name of the project (must exist in Clockify)
   - Optional Parameters:
     * task_id: Specific task ID
     * tags: Comma-separated tag IDs
   - Example: Start a timer with description "Writing documentation" on project "Documentation"

2. get_active_timer
   - Description: Show the currently running timer
   - Parameters: None
   - Returns: Description, project name, duration, and start time
   - Example: Check what timer is currently running

3. stop_timer
   - Description: Stop the currently running timer
   - Parameters: None
   - Returns: Final timer details with total duration
   - Example: Stop the active timer

USAGE EXAMPLES
--------------

In Claude Desktop, you can use natural language:

"Start a timer for 'Coding the API' on project 'Backend Development'"
"Show me my active timer"
"What am I working on right now?"
"Stop my current timer"

NOTES
-----
- All timers are set as billable by default
- Project names are matched case-insensitively
- Duration is calculated and displayed in hours, minutes, and seconds
- The server caches user info and projects on startup for better performance
- Only one timer can be active at a time per user

TROUBLESHOOTING
---------------

Problem: "Error: CLOCKIFY_API_KEY and CLOCKIFY_WORKSPACE_ID must be set"
Solution: Verify your environment variables are correctly set in claude_desktop_config.json

Problem: "Project 'X' not found"
Solution: Verify the project exists in your Clockify workspace and the name matches exactly

Problem: "No active timer to stop"
Solution: Start a timer first using start_timer before trying to stop one

Problem: Server fails to start
Solution: Check Docker logs with: docker logs <container_id>

SECURITY
--------
- API keys are passed as environment variables (never hardcoded)
- Server runs as non-root user in Docker container
- All API communication uses HTTPS
- No data is stored locally; all operations go directly to Clockify API

API DOCUMENTATION
-----------------
For more information about Clockify API:
https://docs.clockify.me/

SUPPORT
-------
For issues or questions, refer to:
- Clockify API docs: https://docs.clockify.me/
- MCP documentation: https://modelcontextprotocol.io/
