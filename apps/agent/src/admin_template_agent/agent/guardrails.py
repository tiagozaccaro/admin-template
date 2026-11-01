DESTRUCTIVE_TOOLS = {"shell", "write_file", "delete_file"}


def check_tool(tool_name: str) -> bool:
    """Return True if tool is allowed without approval."""
    return tool_name not in DESTRUCTIVE_TOOLS


def requires_approval(tool_name: str) -> bool:
    return tool_name in DESTRUCTIVE_TOOLS
