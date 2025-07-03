# py-sse-mcp

[![Build Status](https://github.com/Agent-Hellboy/py-sse-mcp/actions/workflows/python-ci.yml/badge.svg)](https://github.com/Agent-Hellboy/py-sse-mcp/actions/workflows/python-ci.yml)
[![codecov](https://codecov.io/gh/Agent-Hellboy/py-sse-mcp/branch/master/graph/badge.svg)](https://codecov.io/gh/Agent-Hellboy/py-sse-mcp)

A Simple Framework for Creating an MCP Server using sse protocol


This project was created after encountering several issues(I faced it while trying cursor as a client) with **sse transport protocol** of [modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk). The basic setup was inspired by [b3nelof0n/node-mcp-server](https://github.com/b3nelof0n/node-mcp-server/blob/main/server.js).

## Usage

To see detailed debug logs from the framework, configure logging in your application before importing or running the server:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```



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

The framework provides a FastAPI app instance (`pymcp.server.app`). You can use this app to run your server with Uvicorn:

```python
from pymcp.server import app
import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8088)
```

## Configuring Middleware

You can add custom middleware to the FastAPI app provided by the framework. For example, to add a custom middleware:

```python
from pymcp.server import app
from fastapi import Request

@app.middleware("http")
async def custom_middleware(request: Request, call_next):
    # Custom logic before request
    response = await call_next(request)
    # Custom logic after request
    return response
```

You can add this before running the server with Uvicorn as shown above.

Request flow of an example mcp server 
![mcp](./mcp.png)

## Logging

By default, the framework does not configure logging. To see debug or info logs from the framework, configure logging in your application (before importing or running the server):

```python
import logging
logging.basicConfig(level=logging.DEBUG)  # or INFO, WARNING, etc.
```

This allows you to control the verbosity and destination of log messages from both your code and the framework.




