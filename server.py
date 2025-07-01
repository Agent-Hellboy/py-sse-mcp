# ================================ 
# MCP flow:
# 1. Client connects to /sse-cursor (opens SSE connection)
# 2. Server creates a sessionId and starts streaming events to the client
# 3. Client sends a command (e.g., initialize, tools/list, tools/call) to /message?sessionId=...
# 4. Server processes the command and, if needed, puts a response in the session's queue
# 5. Server streams the response/event to the client via the open SSE connection
# 6. Client receives the response/event from the server
# 7. Steps 3-6 repeat for further client commands

#=================================
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
from starlette.middleware.base import BaseHTTPMiddleware
from uuid import uuid4
import asyncio
import json
from typing import Dict, Any
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

app = FastAPI(middleware=[Middleware(CORSMiddleware, allow_origins=["*"])])

# Simple logging middleware
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        return response

app.add_middleware(LoggingMiddleware)

@app.get("/")
async def root():
    return {"status": "ok"}

# Use app.state for sessions to avoid global state issues
def get_sessions(app: FastAPI) -> Dict[str, Dict[str, Any]]:
    if not hasattr(app.state, "sessions"):
        app.state.sessions = {}
    return app.state.sessions

@app.get("/sse-cursor")
async def sse_cursor(request: Request):
    session_id = str(uuid4())
    print(f"[MCP] SSE => /sse-cursor connected")
    print(f"[MCP] Created sessionId: {session_id}")

    queue = asyncio.Queue()
    sessions = get_sessions(app)
    sessions[session_id] = {"initialized": False, "queue": queue}

    async def event_stream():
        # Initial endpoint message
        yield f"event: endpoint\ndata: /message?sessionId={session_id}\n\n"
        
        # Heartbeat every 10 seconds
        while True:
            if await request.is_disconnected():
                print(f"[MCP] SSE closed => sessionId={session_id}")
                sessions.pop(session_id, None)
                break

            try:
                msg = await asyncio.wait_for(queue.get(), timeout=10)
                yield f"event: message\ndata: {msg}\n\n"
            except asyncio.TimeoutError:
                yield f"event: heartbeat\ndata: {int(asyncio.get_event_loop().time())}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")

@app.post("/message")
async def message(request: Request):
    session_id = request.query_params.get("sessionId")
    sessions = get_sessions(app)
    if not session_id or session_id not in sessions:
        return JSONResponse(status_code=404, content={"error": "Invalid or missing sessionId"})

    data = await request.json()
    print(f"[MCP] POST /message => body: {data} query: {session_id}")

    rpc_id = data.get("id")
    method = data.get("method")
    queue = sessions[session_id]["queue"]

    if not method or data.get("jsonrpc") != "2.0":
        return JSONResponse(content={
            "jsonrpc": "2.0",
            "id": rpc_id or None,
            "error": {"code": -32600, "message": "Invalid JSON-RPC request"}
        })

    # Send HTTP ack
    ack = {"jsonrpc": "2.0", "id": rpc_id, "result": {"ack": f"Received {method}"}}
    await handle_rpc_method(method, data, session_id, rpc_id, sessions)
    return JSONResponse(content=ack)

async def handle_rpc_method(method: str, data: dict, session_id: str, rpc_id: Any, sessions: dict):
    queue = sessions[session_id]["queue"]
    if method == "initialize":
        sessions[session_id]["initialized"] = True
        result = {
            "jsonrpc": "2.0",
            "id": rpc_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {"listChanged": True},
                    "resources": {"subscribe": True, "listChanged": True},
                    "prompts": {"listChanged": True},
                    "logging": {}
                },
                "serverInfo": {"name": "final-capabilities-server", "version": "1.0.0"}
            }
        }
        await queue.put(json.dumps(result))

    elif method == "tools/list":
        result = {
            "jsonrpc": "2.0",
            "id": rpc_id,
            "result": {
                "tools": [{
                    "name": "addNumbersTool",
                    "description": "Adds two numbers 'a' and 'b' and returns their sum.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "a": {"type": "number"},
                            "b": {"type": "number"}
                        },
                        "required": ["a", "b"]
                    }
                }],
                "count": 1
            }
        }
        await queue.put(json.dumps(result))

    elif method == "tools/call":
        tool_name = data.get("params", {}).get("name")
        args = data.get("params", {}).get("arguments", {})
        if tool_name == "addNumbersTool":
            a = args.get("a", 0)
            b = args.get("b", 0)
            sum_result = {
                "jsonrpc": "2.0",
                "id": rpc_id,
                "result": {
                    "content": [{
                        "type": "text",
                        "text": f"Sum of {a} + {b} = {a + b}"
                    }]
                }
            }
            await queue.put(json.dumps(sum_result))
        else:
            error = {
                "jsonrpc": "2.0",
                "id": rpc_id,
                "error": {
                    "code": -32601,
                    "message": f"No such tool '{tool_name}'"
                }
            }
            await queue.put(json.dumps(error))

    elif method == "notifications/initialized":
        print(f"[MCP] notifications/initialized => sessionId= {session_id}")
        # No SSE needed

    else:
        error = {
            "jsonrpc": "2.0",
            "id": rpc_id,
            "error": {
                "code": -32601,
                "message": f"Method '{method}' not recognized"
            }
        }
        await queue.put(json.dumps(error))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8008)