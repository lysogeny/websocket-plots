#!/usr/bin/env python3

"""A display client that just prints the message. Useful for testing procedures"""

import json
import asyncio
import websockets
import random
import argparse

async def send(socket, data):
    """Send a message on a socket"""
    msg = json.dumps(data)
    print(f"< {msg}")
    await socket.send(msg)

async def get(msg) -> dict:
    """Send a message on a socket"""
    print(f"> {msg}")
    data = json.loads(msg)
    return data

class Display:
    def __init__(self, uri):
        self.uri = uri
        self.get_size()

    def get_size(self):
        """Gets own size"""
        self.size = tuple(random.randrange(0, 1000) for i in range(0, 2))

    @property
    def msg_register(self):
        return {"msg_type": "register",
                "client_type": "display",
                "size": self.size}
    @property
    def msg_update(self):
        return {"msg_type": "update",
                "size": self.size}

    async def run(self):
        """Client logic"""
        async with websockets.connect(self.uri) as socket:
            # Register client
            await send(socket, self.msg_register)
            async for message in socket:
                data = await get(message)
                if random.random() > 0.5:
                    self.get_size()
                    await send(socket, self.msg_update)
                    #await socket.send(json.dumps(self.msg_update))

def main():
    """Setup parser"""
    parser = argparse.ArgumentParser(description="dumb display client")
    parser.add_argument("-u", "--uri", help="URI", default="ws://localhost:6789")
    args = parser.parse_args()
    # Setup display
    display = Display(args.uri)
    asyncio.get_event_loop().run_until_complete(display.run())
    asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    main()
