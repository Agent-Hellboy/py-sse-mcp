import inspect


class ToolRegistry:
    def __init__(self):
        self._tools = {}

    def register(self, func):
        name = func.__name__
        doc = func.__doc__ or ""
        sig = inspect.signature(func)
        input_schema = {"type": "object", "properties": {}, "required": []}
        for param, value in sig.parameters.items():
            typ = value.annotation
            if typ is int or typ is float:
                typ_str = "number"
            elif typ is str:
                typ_str = "string"
            elif typ is bool:
                typ_str = "boolean"
            else:
                typ_str = "string"
            input_schema["properties"][param] = {"type": typ_str}
            input_schema["required"].append(param)
        has_prompt = "prompt" in sig.parameters
        self._tools[name] = {
            "function": func,
            "description": doc,
            "inputSchema": input_schema,
            "prompt": has_prompt,
        }
        return func

    def get_tools(self):
        return self._tools


tool_registry = ToolRegistry()
