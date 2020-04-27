"""
Helpers for websockets. json loading and dumping for messages received and sent
through websockets. Also prints.

Will be replaced by an abstract base class for client/servers.
"""
import json

async def send(socket, data: dict):
    """Send a message on a socket"""
    msg = json.dumps(data)
    print(f"< {msg}")
    await socket.send(msg)

async def get(msg) -> dict:
    """Send a message on a socket"""
    print(f"> {msg}")
    data = json.loads(msg)
    return data
