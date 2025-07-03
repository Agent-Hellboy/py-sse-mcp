# Framework Middleware Configuration Guide

This guide explains how to configure middleware in your framework using the provided `MiddlewareConfig` class or via keyword arguments.

## Default Middleware

The framework includes the following middleware by default:

- **CORS**: Allows cross-origin requests (default: all origins, all methods, all headers).
- **Logging**: Basic request/response logging (default: INFO level).
- **Error Handling**: Basic error handling to prevent leaking internal details.

Optional middleware you can enable/configure:
- **Compression**: GZip compression for responses.
- **Custom Middleware**: Add your own FastAPI-compatible middleware.

---

## Configuration Methods

You can configure middleware in two ways:

### 1. Using `MiddlewareConfig`

```python
from pymcp.server import create_app, MiddlewareConfig

config = MiddlewareConfig(
    cors={
        "allow_origins": ["https://myapp.com"],
        "allow_methods": ["GET", "POST"],
        "allow_headers": ["*"],
        "allow_credentials": True,
    },
    logging={
        "level": "DEBUG",
        "format": "%(asctime)s %(levelname)s %(message)s",
    },
    error_handling={
        # Add custom error handlers if needed
    },
    compression={
        "enabled": True
    },
    custom=[
        # List of custom middleware classes
    ]
)

app = create_app(middleware_config=config)
```

### 2. Using Keyword Arguments

```python
from pymcp.server import create_app

app = create_app(
    cors={
        "allow_origins": ["https://myapp.com"],
        "allow_methods": ["GET", "POST"],
        "allow_headers": ["*"],
        "allow_credentials": True,
    },
    logging={
        "level": "DEBUG",
        "format": "%(asctime)s %(levelname)s %(message)s",
    },
    compression={
        "enabled": True
    },
    custom=[
        # List of custom middleware classes
    ]
)
```

---

## Middleware Options

### CORS
- `allow_origins`: List of allowed origins (default: `["*"]`)
- `allow_methods`: List of allowed HTTP methods (default: `["*"]`)
- `allow_headers`: List of allowed headers (default: `["*"]`)
- `allow_credentials`: Allow credentials (default: `True`)

### Logging
- `level`: Log level (default: `"INFO"`)
- `format`: Log format string

### Error Handling
- `custom_handler`: (Optional) Your custom error handler function

### Compression
- `enabled`: Enable GZip compression (default: `False`)

### Custom Middleware
- `custom`: List of FastAPI-compatible middleware classes to add

---

## Example: Adding Custom Middleware

```python
from starlette.middleware.base import BaseHTTPMiddleware

class MyCustomMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Custom logic here
        response = await call_next(request)
        return response

config = MiddlewareConfig(custom=[MyCustomMiddleware])
app = create_app(middleware_config=config)
```

---

## Best Practices
- Restrict CORS origins in production.
- Use appropriate log levels for your environment.
- Add custom error handlers for user-friendly error messages.
- Enable compression for large responses or slow networks.
- Add custom middleware for authentication, metrics, etc.

---

## Recommended Usage: config.py

For best practice, create a `config.py` file in your project root to define your middleware configuration. Then, import this config in your server entry point (e.g., `run_server.py`).

### Example: config.py

```python

from pymcp.applications import create_app
from pymcp.middleware import MiddlewareConfig

middleware_config = MiddlewareConfig(
    cors={
        "allow_origins": ["https://myapp.com"],
        "allow_methods": ["GET", "POST"],
        "allow_headers": ["*"],
        "allow_credentials": True,
    },
    logging={
        "level": "DEBUG",
        "format": "%(asctime)s %(levelname)s %(message)s",
    },
    compression={
        "enabled": True
    },
    custom=[
        # Add custom middleware classes here if needed
    ]
)
```

### Example: run_server.py

```python
from config import middleware_config
from pymcp.server import create_app

app = create_app(middleware_config=middleware_config)
```

This approach keeps your configuration clean and separated from your application logic.

For more details, see the framework documentation or contact the maintainers. 