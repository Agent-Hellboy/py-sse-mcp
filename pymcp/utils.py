"""
Utility functions for the MCP framework.
"""

import json
import logging

from .registry import tool_registry


async def handle_rpc_method(method, data, session_id, rpc_id, sessions):
    """
    Handle JSON-RPC methods for the MCP server.
    """
    queue = sessions[session_id]["queue"]
    if method == "initialize":
        sessions[session_id]["initialized"] = True
        result = {
            "jsonrpc": "2.0",
            "id": rpc_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {"listChanged": True}},
                "serverInfo": {"name": "mcpframework", "version": "1.0.0"},
            },
        }
        await queue.put(json.dumps(result))
    elif method == "tools/list":
        tools_list = []
        for tool_name, tool_info in tool_registry.get_tools().items():
            tools_list.append(
                {
                    "name": tool_name,
                    "description": tool_info["description"],
                    "inputSchema": tool_info["inputSchema"],
                    "prompt": tool_info.get("prompt", False),
                }
            )
        result = {
            "jsonrpc": "2.0",
            "id": rpc_id,
            "result": {"tools": tools_list, "count": len(tools_list)},
        }
        logging.debug(f"[TOOLS] Sending {len(tools_list)} tools to Cursor")
        logging.debug(f"[TOOLS] Tool names: {[t['name'] for t in tools_list]}")
        logging.debug(f"[TOOLS] Tool schemas: {json.dumps(tools_list, indent=2)}")
        await queue.put(json.dumps(result))
    elif method == "tools/call":
        tool_name = data.get("params", {}).get("name")
        args = data.get("params", {}).get("arguments", {})
        tools = tool_registry.get_tools()
        if tool_name in tools:
            try:
                result_text = tools[tool_name]["function"](**args)
                success_result = {
                    "jsonrpc": "2.0",
                    "id": rpc_id,
                    "result": {"content": [{"type": "text", "text": result_text}]},
                }
                await queue.put(json.dumps(success_result))
            except Exception as e:
                error = {
                    "jsonrpc": "2.0",
                    "id": rpc_id,
                    "error": {
                        "code": -32603,
                        "message": f"Error executing tool '{tool_name}': {str(e)}",
                    },
                }
                await queue.put(json.dumps(error))
        else:
            error = {
                "jsonrpc": "2.0",
                "id": rpc_id,
                "error": {"code": -32601, "message": f"No such tool '{tool_name}'"},
            }
            await queue.put(json.dumps(error))
    else:
        error = {
            "jsonrpc": "2.0",
            "id": rpc_id,
            "error": {"code": -32601, "message": f"Method '{method}' not recognized"},
        }
        await queue.put(json.dumps(error))
