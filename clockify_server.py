#!/usr/bin/env python3
"""
Simple Clockify MCP Server - Time tracking with Clockify API
"""
import os
import sys
import logging
from datetime import datetime, timezone
import httpx
from mcp.server.fastmcp import FastMCP

# Configure logging to stderr
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger("clockify-server")

# Initialize MCP server
mcp = FastMCP("clockify")

# Configuration
API_KEY = os.environ.get("CLOCKIFY_API_KEY", "")
WORKSPACE_ID = os.environ.get("CLOCKIFY_WORKSPACE_ID", "")
BASE_URL = "https://api.clockify.me/api/v1"

# Cache for user and project data
USER_ID = ""
PROJECTS = []

# === UTILITY FUNCTIONS ===

def get_headers():
    """Return headers for Clockify API requests."""
    return {
        "X-Api-Key": API_KEY,
        "Content-Type": "application/json"
    }

async def fetch_user_info():
    """Fetch current user information."""
    global USER_ID
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/user",
                headers=get_headers(),
                timeout=10.0
            )
            response.raise_for_status()
            user_data = response.json()
            USER_ID = user_data.get("id", "")
            logger.info(f"Fetched user ID: {USER_ID}")
            return True
    except Exception as e:
        logger.error(f"Failed to fetch user info: {e}")
        return False

async def fetch_projects():
    """Fetch all projects for the workspace."""
    global PROJECTS
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/workspaces/{WORKSPACE_ID}/projects",
                headers=get_headers(),
                timeout=10.0
            )
            response.raise_for_status()
            PROJECTS = response.json()
            logger.info(f"Fetched {len(PROJECTS)} projects")
            return True
    except Exception as e:
        logger.error(f"Failed to fetch projects: {e}")
        return False

def find_project_by_name(project_name):
    """Find project by name (case-insensitive)."""
    for project in PROJECTS:
        if project.get("name", "").lower() == project_name.lower():
            return project
    return None

def format_duration(start_time_str):
    """Calculate and format duration from start time to now."""
    try:
        start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        duration = now - start_time
        
        hours = int(duration.total_seconds() // 3600)
        minutes = int((duration.total_seconds() % 3600) // 60)
        seconds = int(duration.total_seconds() % 60)
        
        return f"{hours}h {minutes}m {seconds}s"
    except Exception as e:
        logger.error(f"Error calculating duration: {e}")
        return "Unknown"

def get_current_timestamp():
    """Get current timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

# === MCP TOOLS ===

@mcp.tool()
async def start_timer(description: str = "", project_name: str = "", task_id: str = "", tags: str = "") -> str:
    """Start a new Clockify timer with description and project name (required), optional task_id and tags."""
    logger.info(f"Starting timer: {description} on project {project_name}")
    
    if not API_KEY or not WORKSPACE_ID:
        return "❌ Error: CLOCKIFY_API_KEY and CLOCKIFY_WORKSPACE_ID must be set"
    
    if not USER_ID:
        return "❌ Error: User ID not initialized. Server may need to restart."
    
    if not description:
        return "❌ Error: Description is required"
    
    if not project_name:
        return "❌ Error: Project name is required"
    
    # Find project
    project = find_project_by_name(project_name)
    if not project:
        available = ", ".join([p.get("name", "") for p in PROJECTS[:10]])
        return f"❌ Error: Project '{project_name}' not found. Available projects: {available}"
    
    project_id = project.get("id", "")
    
    # Build request body
    body = {
        "start": get_current_timestamp(),
        "description": description,
        "projectId": project_id,
        "billable": True
    }
    
    if task_id:
        body["taskId"] = task_id
    
    if tags:
        tag_list = [tag.strip() for tag in tags.split(",")]
        body["tagIds"] = tag_list
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/workspaces/{WORKSPACE_ID}/time-entries",
                headers=get_headers(),
                json=body,
                timeout=10.0
            )
            response.raise_for_status()
            result = response.json()
            
            return f"✅ Timer started!\nDescription: {description}\nProject: {project_name}\nStart time: {result.get('timeInterval', {}).get('start', 'Unknown')}"
    except Exception as e:
        logger.error(f"Error starting timer: {e}")
        return f"❌ Error starting timer: {str(e)}"

@mcp.tool()
async def get_active_timer() -> str:
    """Show the currently active/running timer with description, duration, and project."""
    logger.info("Fetching active timer")
    
    if not API_KEY or not WORKSPACE_ID:
        return "❌ Error: CLOCKIFY_API_KEY and CLOCKIFY_WORKSPACE_ID must be set"
    
    if not USER_ID:
        return "❌ Error: User ID not initialized. Server may need to restart."
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/workspaces/{WORKSPACE_ID}/user/{USER_ID}/time-entries",
                headers=get_headers(),
                params={"in-progress": "true"},
                timeout=10.0
            )
            response.raise_for_status()
            entries = response.json()
            
            if not entries or len(entries) == 0:
                return "⏸️ No active timer running"
            
            entry = entries[0]
            description = entry.get("description", "No description")
            start_time = entry.get("timeInterval", {}).get("start", "")
            project_id = entry.get("projectId", "")
            
            # Find project name
            project_name = "Unknown project"
            if project_id:
                for project in PROJECTS:
                    if project.get("id") == project_id:
                        project_name = project.get("name", "Unknown project")
                        break
            
            duration = format_duration(start_time)
            
            return f"⏱️ Active Timer:\nDescription: {description}\nProject: {project_name}\nDuration: {duration}\nStarted: {start_time}"
    except Exception as e:
        logger.error(f"Error fetching active timer: {e}")
        return f"❌ Error fetching active timer: {str(e)}"

@mcp.tool()
async def stop_timer() -> str:
    """Stop the currently running timer and return the final details."""
    logger.info("Stopping active timer")
    
    if not API_KEY or not WORKSPACE_ID:
        return "❌ Error: CLOCKIFY_API_KEY and CLOCKIFY_WORKSPACE_ID must be set"
    
    if not USER_ID:
        return "❌ Error: User ID not initialized. Server may need to restart."
    
    try:
        # First check if there's an active timer
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/workspaces/{WORKSPACE_ID}/user/{USER_ID}/time-entries",
                headers=get_headers(),
                params={"in-progress": "true"},
                timeout=10.0
            )
            response.raise_for_status()
            entries = response.json()
            
            if not entries or len(entries) == 0:
                return "⏸️ No active timer to stop"
            
            entry = entries[0]
            description = entry.get("description", "No description")
            start_time = entry.get("timeInterval", {}).get("start", "")
            project_id = entry.get("projectId", "")
            
            # Find project name
            project_name = "Unknown project"
            if project_id:
                for project in PROJECTS:
                    if project.get("id") == project_id:
                        project_name = project.get("name", "Unknown project")
                        break
            
            # Stop the timer
            body = {"end": get_current_timestamp()}
            response = await client.patch(
                f"{BASE_URL}/workspaces/{WORKSPACE_ID}/user/{USER_ID}/time-entries",
                headers=get_headers(),
                json=body,
                timeout=10.0
            )
            response.raise_for_status()
            
            duration = format_duration(start_time)
            
            return f"⏹️ Timer stopped!\nDescription: {description}\nProject: {project_name}\nTotal duration: {duration}"
    except Exception as e:
        logger.error(f"Error stopping timer: {e}")
        return f"❌ Error stopping timer: {str(e)}"

# === SERVER STARTUP ===
if __name__ == "__main__":
    logger.info("Starting Clockify MCP server...")
    
    # Check for required environment variables
    if not API_KEY:
        logger.error("CLOCKIFY_API_KEY not set")
        sys.exit(1)
    
    if not WORKSPACE_ID:
        logger.error("CLOCKIFY_WORKSPACE_ID not set")
        sys.exit(1)
    
    # Initialize user and projects data
    import asyncio
    loop = asyncio.get_event_loop()
    
    if not loop.run_until_complete(fetch_user_info()):
        logger.error("Failed to fetch user info")
        sys.exit(1)
    
    if not loop.run_until_complete(fetch_projects()):
        logger.error("Failed to fetch projects")
        sys.exit(1)
    
    logger.info(f"Initialized with user ID: {USER_ID}")
    logger.info(f"Loaded {len(PROJECTS)} projects")
    
    try:
        mcp.run(transport='stdio')
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)
