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
    compression={"enabled": True},
    custom=[
        # Add custom middleware classes here if needed
    ],
)
