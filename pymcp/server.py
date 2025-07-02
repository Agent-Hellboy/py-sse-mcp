import asyncio
import json
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse

from .registry import tool_registry

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_sessions(app):
    if not hasattr(app.state, "sessions"):
        app.state.sessions = {}
    return app.state.sessions


@app.get("/")
async def root():
    return {"status": "ok"}


@app.get("/sse-cursor")
async def sse_cursor(request: Request):
    session_id = str(uuid4())
    print("[MCP] SSE => /sse-cursor connected")
    print(f"[MCP] Created sessionId: {session_id}")
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


@app.post("/message")
async def message(request: Request):
    session_id = request.query_params.get("sessionId")
    sessions = get_sessions(app)
    if not session_id or session_id not in sessions:
        return JSONResponse(
            status_code=404, content={"error": "Invalid or missing sessionId"}
        )
    data = await request.json()
    print(f"[MCP] POST /message => body: {data} query: {session_id}")
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


async def handle_rpc_method(method, data, session_id, rpc_id, sessions):
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
        print(f"[TOOLS] Sending {len(tools_list)} tools to Cursor")
        print(f"[TOOLS] Tool names: {[t['name'] for t in tools_list]}")
        print(f"[TOOLS] Tool schemas: {json.dumps(tools_list, indent=2)}")
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
