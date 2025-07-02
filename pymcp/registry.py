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


class ResourceRegistry:
    def __init__(self):
        self._resources = []

    def resource(self, uri, name, description=None, mimeType=None):
        def decorator(func):
            self._resources.append({
                "uri": uri,
                "name": name,
                "description": description,
                "mimeType": mimeType,
                "size": None,
                "func": func,
                "path": None
            })
            return func
        return decorator

    def list_resources(self):
        import os
        resources = []
        for res in self._resources:
            # Optionally update size for file-based resources
            if res.get("path") and res["path"] and os.path.exists(res["path"]):
                res["size"] = os.path.getsize(res["path"])
            resources.append({k: v for k, v in res.items() if k not in ("path", "func")})
        return resources

    def read_resource(self, uri):
        import os
        for res in self._resources:
            if res["uri"] == uri:
                if res.get("func"):
                    # Call the function to get the resource content
                    content = res["func"]()
                    return {
                        "uri": uri,
                        "mimeType": res["mimeType"],
                        "text": content
                    }
                elif res.get("path") and res["path"] and os.path.exists(res["path"]):
                    with open(res["path"], "r", encoding="utf-8") as f:
                        text = f.read()
                    return {
                        "uri": uri,
                        "mimeType": res["mimeType"],
                        "text": text
                    }
                else:
                    raise FileNotFoundError(f"Resource not found: {res.get('path', uri)}")
        raise ValueError("Resource not found")

    def register(self, *args, **kwargs):
        return self.add_resource(*args, **kwargs)

resource_registry = ResourceRegistry()

