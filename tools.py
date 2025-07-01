# Tools definition file
# Each tool is defined as a function with metadata
from datetime import datetime

def add_numbers_tool(a: float, b: float) -> str:
    """Adds two numbers and returns their sum."""
    return f"Sum of {a} + {b} = {a + b}"

def multiply_numbers_tool(a: float, b: float) -> str:
    """Multiplies two numbers and returns their product."""
    return f"Product of {a} * {b} = {a * b}"

def greet_tool(name: str) -> str:
    """Greets a person by name."""
    return f"Hello, {name}! Nice to meet you!"

def calculate_area_tool(length: float, width: float) -> str:
    """Calculates the area of a rectangle."""
    area = length * width
    return f"Area of rectangle with length {length} and width {width} = {area}"

def get_current_time_tool() -> str:
    """Returns the current time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Tool registry - maps tool names to their functions and schemas
TOOLS_REGISTRY = {
    "addNumbersTool": {
        "function": add_numbers_tool,
        "description": "Adds two numbers 'a' and 'b' and returns their sum.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "a": {"type": "number"},
                "b": {"type": "number"}
            },
            "required": ["a", "b"]
        }
    },
    "multiplyNumbersTool": {
        "function": multiply_numbers_tool,
        "description": "Multiplies two numbers 'a' and 'b' and returns their product.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "a": {"type": "number"},
                "b": {"type": "number"}
            },
            "required": ["a", "b"]
        }
    },
    "greetTool": {
        "function": greet_tool,
        "description": "Greets a person by their name.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"}
            },
            "required": ["name"]
        }
    },
    "calculateAreaTool": {
        "function": calculate_area_tool,
        "description": "Calculates the area of a rectangle given length and width.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "length": {"type": "number"},
                "width": {"type": "number"}
            },
            "required": ["length", "width"]
        }
    },
    "getCurrentTimeTool": {
        "function": get_current_time_tool,
        "description": "Returns the current time.",
        "inputSchema": {}
    }
} 