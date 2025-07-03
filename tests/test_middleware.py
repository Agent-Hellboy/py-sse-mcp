
from fastapi.testclient import TestClient
from fastapi.responses import PlainTextResponse

class CustomHeaderMiddleware:
    def __init__(self, app):
        self.app = app
    async def __call__(self, scope, receive, send):
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = dict(message.get("headers", []))
                headers[b"x-custom-middleware"] = b"true"
                message["headers"] = list(headers.items())
            await send(message)
        await self.app(scope, receive, send_wrapper)


def test_gzip_and_custom_middleware():
    # Create app with GZip and custom middleware
    from pymcp.applications import create_app
    from pymcp.middleware import MiddlewareConfig
    config = MiddlewareConfig(compression={"enabled": True}, custom=[CustomHeaderMiddleware])
    app = create_app(middleware_config=config)

    @app.get("/plain")
    def plain():
        return PlainTextResponse("Hello World!" * 100)

    client = TestClient(app)
    # Test GZipMiddleware
    resp = client.get("/plain", headers={"Accept-Encoding": "gzip"})
    assert resp.status_code == 200
    assert resp.headers.get("content-encoding") == "gzip"
    # Test custom middleware
    assert resp.headers.get("x-custom-middleware") == "true"