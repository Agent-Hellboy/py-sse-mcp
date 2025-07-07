# py-sse-mcp

**I won't add any new commits except for initial prompts and resource, you can use this as an initial setup to implement your own framework. I am not achiving it as i will add an initial commits fpr resource and prompts**

[![Build Status](https://github.com/Agent-Hellboy/py-sse-mcp/actions/workflows/python-ci.yml/badge.svg)](https://github.com/Agent-Hellboy/py-sse-mcp/actions/workflows/python-ci.yml)
[![codecov](https://codecov.io/gh/Agent-Hellboy/py-sse-mcp/branch/master/graph/badge.svg)](https://codecov.io/gh/Agent-Hellboy/py-sse-mcp)

A Simple Framework for Creating an MCP Server using sse protocol


This project was created after encountering several issues(I faced it while trying cursor as a client) with **sse transport protocol** of [modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk). The basic setup was inspired by [b3nelof0n/node-mcp-server](https://github.com/b3nelof0n/node-mcp-server/blob/main/server.js).

## Usage

Run the example server:
   ```bash
   pip install .
   python example/run_server.py
   ```

**Note:** Targeting Cursor as a client only.

## Writing Your Own Tool

To create a tool with this framework, use the `@tool_registry.register` decorator. For example:

```python
from pymcp.registry import tool_registry

@tool_registry.register
def my_tool(a: int, b: int) -> str:
    """Adds two numbers and returns the result as a string."""
    return f"Result: {a + b}"
```

## Hosting the Server with FastAPI and Uvicorn

The framework provides a FastAPI app factory (`pymcp.applications.create_app`). You can use this to create and configure your server, including middleware and compression:

```python
from pymcp.applications import create_app
import uvicorn

# Example: Enable GZip compression and add custom middleware
from fastapi import Request, Response

class CustomHeaderMiddleware:
    def __init__(self, app):
        self.app = app
    async def __call__(self, scope, receive, send):
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = dict(message.get("headers", []))
                headers[b"x-custom-middleware"] = b"true"
                message["headers"] = list(headers.items())
            await send(message)
        await self.app(scope, receive, send_wrapper)

from pymcp.middleware import MiddlewareConfig

middleware_config = MiddlewareConfig(
    compression={"enabled": True},
    custom=[CustomHeaderMiddleware]
)

app = create_app(middleware_config=middleware_config)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8088)
```

## Configuring Middleware

To add custom or extra middleware (such as GZip, CORS, or your own), use the `MiddlewareConfig` and pass it to `create_app`:

```python
from pymcp.applications import create_app
from pymcp.middleware import MiddlewareConfig

# Example: Add your own custom middleware class
class MyCustomMiddleware:
    def __init__(self, app):
        self.app = app
    async def __call__(self, scope, receive, send):
        # ... your logic ...
        await self.app(scope, receive, send)

middleware_config = MiddlewareConfig(
    compression={"enabled": True},  # Enables GZip
    custom=[MyCustomMiddleware]
)

app = create_app(middleware_config=middleware_config)
```

**Note:**  
- The framework automatically applies CORS and other standard middleware.
- You can stack as many custom middleware as you like using the `custom` list in `MiddlewareConfig`.
- For simple per-route logic, you can still use FastAPI's `@app.middleware("http")` decorator after creating the app, but the preferred way is via `MiddlewareConfig` for global middleware.

Request flow of an example mcp server 
![mcp](./mcp.png)

## Logging

By default, the framework does not configure logging. To see debug or info logs from the framework, configure logging in your application (before importing or running the server):

```python
import logging
logging.basicConfig(level=logging.DEBUG)  # or INFO, WARNING, etc.
```

This allows you to control the verbosity and destination of log messages from both your code and the framework.

## Middleware Configuration

Check [guide.md](./guide.md).




