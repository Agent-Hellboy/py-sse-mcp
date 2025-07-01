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
            if typ == int or typ == float:
                typ_str = "number"
            elif typ == str:
                typ_str = "string"
            elif typ == bool:
                typ_str = "boolean"
            else:
                typ_str = "string"
            input_schema["properties"][param] = {"type": typ_str}
            input_schema["required"].append(param)
        self._tools[name] = {
            "function": func,
            "description": doc,
            "inputSchema": input_schema,
        }
        return func

    def get_tools(self):
        return self._tools


tool_registry = ToolRegistry()
