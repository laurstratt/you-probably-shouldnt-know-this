import asyncio
import os
from pathlib import Path
from http import HTTPStatus
import websockets
from server import handler

PORT = int(os.environ.get("PORT", "8765"))
PUBLIC = Path(__file__).parent / "public"


def process_request(path, request_headers):
    # Normal browser requests are served by the same port as WebSockets.
    # WebSocket upgrade requests continue through to `handler`.
    if path == "/health":
        return HTTPStatus.OK, [("Content-Type", "text/plain; charset=utf-8")], b"ok"
    if path == "/":
        path = "/index.html"
    file = PUBLIC / path.lstrip("/")
    if file.exists() and file.is_file():
        content_type = "text/html; charset=utf-8"
        if file.suffix == ".css":
            content_type = "text/css; charset=utf-8"
        elif file.suffix == ".js":
            content_type = "application/javascript; charset=utf-8"
        return HTTPStatus.OK, [("Content-Type", content_type)], file.read_bytes()
    return HTTPStatus.NOT_FOUND, [("Content-Type", "text/plain; charset=utf-8")], b"Not found"


async def main():
    async with websockets.serve(
        handler,
        "0.0.0.0",
        PORT,
        process_request=process_request,
        ping_interval=20,
        ping_timeout=20,
    ):
        print(f"You Probably Shouldn't Know This listening on port {PORT}")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
