"""
Middleware configuration and setup for the MCP framework.
"""

from typing import Any, Dict, Optional

from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware


class MiddlewareConfig:
    """
    Configuration class for setting up middleware in the MCP server.
    """

    def __init__(
        self,
        cors: Optional[Dict[str, Any]] = None,
        logging: Optional[Dict[str, Any]] = None,
        error_handling: Optional[Dict[str, Any]] = None,
        compression: Optional[Dict[str, Any]] = None,
        custom: Optional[list] = None,
    ):
        self.cors = cors or {
            "allow_origins": ["*"],
            "allow_credentials": True,
            "allow_methods": ["*"],
            "allow_headers": ["*"],
        }
        self.logging = logging or {
            "level": "INFO",
            "format": "%(asctime)s %(levelname)s %(message)s",
        }
        self.error_handling = error_handling or {}
        self.compression = compression or {"enabled": False}
        self.custom = custom or []


def setup_middleware(app, config: MiddlewareConfig):
    """
    Apply middleware to the FastAPI app based on the provided MiddlewareConfig.
    """
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors["allow_origins"],
        allow_credentials=config.cors["allow_credentials"],
        allow_methods=config.cors["allow_methods"],
        allow_headers=config.cors["allow_headers"],
    )

    # Compression
    if config.compression.get("enabled", False):
        app.add_middleware(GZipMiddleware)
    # Custom middleware
    for mw in config.custom:
        if not callable(mw):
            raise ValueError(f"Custom middleware {mw} is not callable")
        app.add_middleware(mw)
    # Error handling can be added here as needed
