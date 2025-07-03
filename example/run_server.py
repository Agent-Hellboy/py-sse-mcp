import logging

from config import middleware_config
from pymcp.applications import create_app
from pymcp.registry import tool_registry

logging.basicConfig(level=logging.DEBUG)


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


@tool_registry.register
def promptEchoTool(prompt: str) -> str:
    """Echoes back the prompt provided, with input validation."""
    if not prompt or "crash" in prompt.lower():
        return "Invalid input. Please try again."
    return f"You said: {prompt}"


if __name__ == "__main__":
    import uvicorn

    app = create_app(middleware_config=middleware_config)
    uvicorn.run(app, host="0.0.0.0", port=8088)
