# py-sse-mcp

[![Build Status](https://github.com/Agent-Hellboy/py-sse-mcp/actions/workflows/python-ci.yml/badge.svg)](https://github.com/Agent-Hellboy/py-sse-mcp/actions/workflows/python-ci.yml)
[![codecov](https://codecov.io/gh/Agent-Hellboy/py-sse-mcp/branch/master/graph/badge.svg)](https://codecov.io/gh/Agent-Hellboy/py-sse-mcp)

A Simple Framework for Creating an MCP Server using sse protocol

## Usage

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the example server:
   ```bash
   pip install .
   python example/run_server.py
   ```

**Note:** Tested only with Cursor.

This project was created after encountering several issues with **sse transport protocol** [modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk). The basic setup was inspired by [b3nelof0n/node-mcp-server](https://github.com/b3nelof0n/node-mcp-server/blob/main/server.js).

Request flow of an example mcp server 
![mcp](./mcp.png)


