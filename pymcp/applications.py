"""
App factory for the MCP framework.
Provides the create_app function to instantiate and configure the FastAPI app.
"""

from typing import Optional

from fastapi import FastAPI

from .middleware import MiddlewareConfig, setup_middleware
from .server import router


def create_app(middleware_config: Optional[MiddlewareConfig] = None, **kwargs):
    app = FastAPI()
    config = middleware_config or MiddlewareConfig(
        cors=kwargs.get("cors"),
        logging=kwargs.get("logging"),
        error_handling=kwargs.get("error_handling"),
        compression=kwargs.get("compression"),
        custom=kwargs.get("custom"),
    )
    setup_middleware(app, config)
    app.include_router(router)
    return app
