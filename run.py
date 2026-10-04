import asyncio
from pathlib import Path
from websockets.server import serve
from websockets.http11 import Response
import server

PUBLIC = Path(__file__).parent / "public"

async def process_request(path, request_headers):
    if path == "/health":
        body = b"ok\n"
        return Response(200, "OK", [("Content-Type", "text/plain"), ("Content-Length", str(len(body)))], body)
    if path == "/" or path == "/index.html":
        body = (PUBLIC / "index.html").read_bytes()
        return Response(200, "OK", [("Content-Type", "text/html; charset=utf-8"), ("Content-Length", str(len(body)))], body)
    return None

async def main():
    # One listener handles BOTH ordinary browser HTTP requests and WebSocket upgrades.
    # Do not start server.http_server separately: it would compete for the same port.
    async with serve(
        server.handler,
        "0.0.0.0",
        server.PORT,
        process_request=process_request,
    ):
        print(f"You Probably Shouldn't Know This running on port {server.PORT}", flush=True)
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
