# CLOCKIFY MCP SERVER - IMPLEMENTATION GUIDE

## Overview
This MCP server provides Clockify time tracking integration with three core tools: start_timer, get_active_timer, and stop_timer.

## Architecture

### Server Initialization
The server performs the following on startup:
1. Validates environment variables (CLOCKIFY_API_KEY, CLOCKIFY_WORKSPACE_ID)
2. Fetches current user information from Clockify API
3. Loads and caches all workspace projects
4. Stores user ID and project list in memory for quick access

### API Integration
- Base URL: https://api.clockify.me/api/v1
- Authentication: API key via X-Api-Key header
- All requests use JSON content type
- Timeout: 10 seconds per request

### Data Flow

**start_timer:**
1. Validate required parameters (description, project_name)
2. Search cached projects for case-insensitive match
3. Build request body with current timestamp as start time
4. POST to /workspaces/{workspaceId}/time-entries
5. Return success confirmation with timer details

**get_active_timer:**
1. GET /workspaces/{workspaceId}/user/{userId}/time-entries?in-progress=true
2. If no entries, return "No active timer"
3. Calculate duration from start time to current time
4. Match project ID to cached project name
5. Return formatted timer information

**stop_timer:**
1. Fetch active timer (same as get_active_timer)
2. If no active timer, return error
3. PATCH /workspaces/{workspaceId}/time-entries/{entryId} with end timestamp
4. Return final duration and details

## Key Design Decisions

### Project Lookup
- Projects are cached on startup to avoid repeated API calls
- Case-insensitive matching allows flexible project name input
- If project not found, first 10 available projects are shown

### Time Handling
- All timestamps use ISO 8601 format with UTC timezone
- Duration calculated client-side from start time to current time
- Format: "Xh Ym Zs" for human readability

### Error Handling
- Graceful degradation with user-friendly error messages
- All exceptions logged to stderr for debugging
- API errors include status code information

### Billable Status
- All time entries default to billable=true per requirements
- This cannot be changed via the tools

## Tool Specifications

### start_timer
```python
Parameters:
  - description: str (required) - What you're working on
  - project_name: str (required) - Project to track time to
  - task_id: str (optional) - Specific task identifier
  - tags: str (optional) - Comma-separated tag IDs

Returns: String with success/error message
```

### get_active_timer
```python
Parameters: None

Returns: String with timer details or "No active timer"
```

### stop_timer
```python
Parameters: None

Returns: String with final timer details or error
```

## Usage in Claude

Claude can invoke these tools naturally:

**Starting timers:**
- "Start a timer for 'Writing tests' on project 'QA'"
- "Begin tracking time on 'Code review' for project 'Backend'"

**Checking status:**
- "What am I working on?"
- "Show my current timer"
- "How long have I been on this task?"

**Stopping timers:**
- "Stop my timer"
- "End the current time entry"

## Best Practices

### When to Use Each Tool
- Use start_timer when beginning work on a task
- Use get_active_timer to check progress or verify what's running
- Use stop_timer when completing a task or taking a break

### Project Names
- Ensure project exists in Clockify before starting timer
- Use exact names (case-insensitive matching supported)
- If unsure, start a timer - the error will list available projects

### Multiple Timers
- Only one timer can run at a time per user
- Starting a new timer while one is active will fail
- Always stop current timer before starting a new one

## Limitations

1. **Single User:** Server assumes single user per workspace
2. **Project Matching:** Only matches by name, not by ID
3. **No Timer Editing:** Cannot modify running or past timers
4. **Tag Input:** Tags must be provided as IDs, not names
5. **Task Assignment:** Tasks must be provided as IDs, not names

## Troubleshooting

### Server Won't Start
- Verify Docker is running
- Check API key and workspace ID are valid
- Review Docker logs: `docker logs <container_id>`

### Project Not Found
- Verify project exists in Clockify workspace
- Check spelling (case-insensitive but must match)
- Look at available projects in error message

### Timer Issues
- Verify only one timer is running at a time
- Check network connectivity to Clockify API
- Ensure workspace ID matches the workspace containing projects

## Security Considerations

1. **API Key Protection:** Never commit API keys to version control
2. **Environment Variables:** Keys passed securely via Docker env vars
3. **Non-Root User:** Container runs as non-root user (mcpuser)
4. **HTTPS Only:** All API communication uses secure HTTPS
5. **No Local Storage:** No sensitive data stored in container

## Development Notes

### Testing
- Test with actual Clockify workspace before deploying
- Verify project names match exactly what's in Clockify
- Test error scenarios (missing project, no active timer, etc.)

### Customization
- Modify billable status logic in start_timer if needed
- Adjust duration format in format_duration function
- Add additional fields to timer display as desired

### Extending Functionality
To add new tools:
1. Add new @mcp.tool() decorated function
2. Use single-line docstring
3. Return formatted string
4. Handle errors gracefully
5. Update readme.txt and CLAUDE.md

## API Endpoints Used

1. GET /v1/user - Fetch current user information
2. GET /v1/workspaces/{workspaceId}/projects - List all projects
3. POST /v1/workspaces/{workspaceId}/time-entries - Create time entry
4. GET /v1/workspaces/{workspaceId}/user/{userId}/time-entries - Get time entries
5. PATCH /v1/workspaces/{workspaceId}/time-entries/{id} - Update time entry

## Dependencies

- mcp[cli]>=1.2.0 - MCP framework and CLI support
- httpx - Async HTTP client for API requests
- Python 3.11 - Runtime environment

## Performance Considerations

- Projects cached on startup (reduces API calls)
- User ID cached after first fetch
- Each tool use makes 1-2 API calls maximum
- Async operations for non-blocking I/O
- 10-second timeout prevents hanging requests

## Future Enhancements

Potential improvements:
- Support for listing recent time entries
- Edit description of running timer
- Support for tags by name (not just ID)
- Project search/filtering capabilities
- Multiple workspace support
- Timer templates for common tasks
