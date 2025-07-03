import os
import sys

import pytest
import requests

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import time
from threading import Thread

import uvicorn

from pymcp.registry import tool_registry
from pymcp.applications import create_app

BASE_URL = "http://127.0.0.1:8088"


@pytest.fixture(scope="session", autouse=True)
def start_server():
    # Start the server in a background thread
    server = Thread(
        target=uvicorn.run,
        args=(create_app(middleware_config=None),),
        kwargs={"host": "127.0.0.1", "port": 8088},
        daemon=True,
    )
    server.start()
    time.sleep(1)
    yield


@tool_registry.register
def addNumbersTool(a: float, b: float) -> str:
    return f"Sum of {a} + {b} = {a + b}"


@tool_registry.register
def multiplyNumbersTool(a: float, b: float) -> str:
    return f"Product of {a} * {b} = {a * b}"


@tool_registry.register
def greetTool(name: str) -> str:
    return f"Hello, {name}! Nice to meet you!"


@tool_registry.register
def calculateAreaTool(length: float, width: float) -> str:
    area = length * width
    return f"Area of rectangle with length {length} and width {width} = {area}"


@tool_registry.register
def promptEchoTool(prompt: str) -> str:
    """Echoes back the prompt provided."""
    return f"You said: {prompt}"


def test_root():
    resp = requests.get(f"{BASE_URL}/")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_sse_cursor():
    try:
        resp = requests.get(f"{BASE_URL}/sse-cursor", stream=True, timeout=5)
    except requests.ConnectionError:
        pytest.fail(
            "Server is not running on 127.0.0.1:8088. Please start it before running tests."
        )
    session_id = None
    for line in resp.iter_lines():
        if line:
            decoded = line.decode()
            if decoded.startswith("data: /message?sessionId="):
                session_id = decoded.split("=")[-1]
                break
    assert session_id
    return session_id


def test_full_flow():
    try:
        resp = requests.get(f"{BASE_URL}/sse-cursor", stream=True, timeout=5)
    except requests.ConnectionError:
        pytest.fail(
            "Server is not running on 127.0.0.1:8088. Please start it before running tests."
        )
    session_id = None
    for line in resp.iter_lines():
        if line:
            decoded = line.decode()
            if decoded.startswith("data: /message?sessionId="):
                session_id = decoded.split("=")[-1]
                break
    assert session_id

    # Initialize
    payload = {"jsonrpc": "2.0", "id": 1, "method": "initialize"}
    resp = requests.post(f"{BASE_URL}/message?sessionId={session_id}", json=payload)
    assert resp.status_code == 200
    assert resp.json()["result"]["ack"] == "Received initialize"

    # List tools
    payload = {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}
    resp = requests.post(f"{BASE_URL}/message?sessionId={session_id}", json=payload)
    assert resp.status_code == 200
    assert resp.json()["result"]["ack"] == "Received tools/list"

    # Call a tool
    payload = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {"name": "addNumbersTool", "arguments": {"a": 2, "b": 3}},
    }
    resp = requests.post(f"{BASE_URL}/message?sessionId={session_id}", json=payload)
    assert resp.status_code == 200
    assert "content" in resp.json()["result"]
    assert resp.json()["result"]["content"][0]["text"] == "Sum of 2 + 3 = 5"


def test_tools_list_includes_prompt():
    resp = requests.get(f"{BASE_URL}/sse-cursor", stream=True, timeout=5)
    session_id = None
    for line in resp.iter_lines():
        if line:
            decoded = line.decode()
            if decoded.startswith("data: /message?sessionId="):
                session_id = decoded.split("=")[-1]
                break
    assert session_id
    payload = {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}
    resp = requests.post(f"{BASE_URL}/message?sessionId={session_id}", json=payload)
    assert resp.status_code == 200
    tools = resp.json()["result"].get("tools", [])
    for tool in tools:
        if tool["name"] == "promptEchoTool":
            assert tool["prompt"] is True


def test_prompt_echo_tool():
    resp = requests.get(f"{BASE_URL}/sse-cursor", stream=True, timeout=5)
    session_id = None
    for line in resp.iter_lines():
        if line:
            decoded = line.decode()
            if decoded.startswith("data: /message?sessionId="):
                session_id = decoded.split("=")[-1]
                break
    assert session_id
    payload = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {"name": "promptEchoTool", "arguments": {"prompt": "Hello!"}},
    }
    resp = requests.post(f"{BASE_URL}/message?sessionId={session_id}", json=payload)
    assert resp.status_code == 200
    result = resp.json()["result"]["content"][0]["text"]
    assert result == "You said: Hello!"
