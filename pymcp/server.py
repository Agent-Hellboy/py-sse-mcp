"""
Main server logic for the MCP framework.
"""

import asyncio
import json
import logging
from uuid import uuid4

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, StreamingResponse

from .registry import tool_registry
from .utils import handle_rpc_method

router = APIRouter()


def get_sessions(app):
    if not hasattr(app.state, "sessions"):
        app.state.sessions = {}
    return app.state.sessions


@router.get("/")
async def root():
    return {"status": "ok"}


@router.get("/sse-cursor")
async def sse_cursor(request: Request):
    app = request.app
    session_id = str(uuid4())
    logging.debug("[MCP] SSE => /sse-cursor connected")
    logging.debug(f"[MCP] Created sessionId: {session_id}")
    queue = asyncio.Queue()
    sessions = get_sessions(app)
    sessions[session_id] = {"initialized": False, "queue": queue}

    async def event_stream():
        yield f"event: endpoint\ndata: /message?sessionId={session_id}\n\n"
        while True:
            if await request.is_disconnected():
                sessions.pop(session_id, None)
                break
            try:
                msg = await asyncio.wait_for(queue.get(), timeout=10)
                yield f"event: message\ndata: {msg}\n\n"
            except asyncio.TimeoutError:
                yield "event: heartbeat\ndata: ping\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.post("/message")
async def message(request: Request):
    app = request.app
    session_id = request.query_params.get("sessionId")
    sessions = get_sessions(app)
    if not session_id or session_id not in sessions:
        return JSONResponse(
            status_code=404, content={"error": "Invalid or missing sessionId"}
        )
    data = await request.json()
    logging.debug(f"[MCP] POST /message => method: {data.get('method', 'unknown')} query: {session_id}")
    rpc_id = data.get("id")
    method = data.get("method")
    queue = sessions[session_id]["queue"]

    if not method or data.get("jsonrpc") != "2.0":
        return JSONResponse(
            content={
                "jsonrpc": "2.0",
                "id": rpc_id or None,
                "error": {"code": -32600, "message": "Invalid JSON-RPC request"},
            }
        )

    # Special handling for tools/call to return result directly
    if method == "tools/call":
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
                # Stream to SSE clients as before
                await queue.put(json.dumps(success_result))
                # Return result directly in HTTP response
                return JSONResponse(content=success_result)
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
                return JSONResponse(content=error)
        else:
            error = {
                "jsonrpc": "2.0",
                "id": rpc_id,
                "error": {"code": -32601, "message": f"No such tool '{tool_name}'"},
            }
            await queue.put(json.dumps(error))
            return JSONResponse(content=error)
    # Default: keep old behavior for other methods
    ack = {"jsonrpc": "2.0", "id": rpc_id, "result": {"ack": f"Received {method}"}}
    await handle_rpc_method(method, data, session_id, rpc_id, sessions)
    return JSONResponse(content=ack)
