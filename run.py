import asyncio
import threading
from websockets.server import serve
import server

async def main():
    threading.Thread(target=server.http_server, daemon=True).start()
    async with serve(server.handler, "0.0.0.0", server.PORT):
        print(f"You Probably Shouldn't Know This running on port {server.PORT}", flush=True)
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
