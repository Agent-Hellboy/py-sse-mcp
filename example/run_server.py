import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from pymcp.registry import tool_registry
from pymcp.server import app


@tool_registry.register
def addNumbersTool(a: float, b: float) -> str:
    """Adds two numbers 'a' and 'b' and returns their sum."""
    return f"Sum of {a} + {b} = {a + b}"


@tool_registry.register
def multiplyNumbersTool(a: float, b: float) -> str:
    """Multiplies two numbers 'a' and 'b' and returns their product."""
    return f"Product of {a} * {b} = {a * b}"


@tool_registry.register
def greetTool(name: str) -> str:
    """Greets a person by their name."""
    return f"Hello, {name}! Nice to meet you!"


@tool_registry.register
def calculateAreaTool(length: float, width: float) -> str:
    """Calculates the area of a rectangle given length and width."""
    area = length * width
    return f"Area of rectangle with length {length} and width {width} = {area}"


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8088)
