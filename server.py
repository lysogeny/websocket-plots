#!/usr/bin/env python3

"""A display client that just prints the message. Useful for testing procedures"""

import json
import asyncio
import websockets
import random
import argparse

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

class Server:
    def __init__(self, port=6789, host="localhost"):
        self.port = port
        self.host = host
        self.clients = dict()
        # {client: (w, h)}
        self.plots = dict()
        # {(w, h): str}

    @property
    def msg_sizes(self):
        return {"msg_type": "sizes", "sizes": list(set(self.clients.values()))}

    async def send_plot(self, websocket):
        if self.clients[websocket] not in self.plots:
            # If there is no plot we can't just magic it out of thin air.
            # Thus I just make some empty SVG tags.
            self.plots[self.clients[websocket]] = "<SVG></SVG>"
        data = {"msg_type": "plot", "text": self.plots[self.clients[websocket]]}
        await send(websocket, data)

    async def run_display(self, websocket, data):
        """Logic for display type clients"""
        # First register them
        self.clients[websocket] = tuple(data["size"])
        print(f"Registered {websocket.remote_address[0]}:{websocket.remote_address[1]} {self.clients[websocket]}")
        await self.send_plot(websocket)
        try:
            async for message in websocket:
                # Then wait for resizes
                data = await get(message)
                if data["msg_type"] == "update":
                    self.clients[websocket] = tuple(data["size"])
                    if self.clients[websocket] in self.plots:
                        await self.send_plot(websocket)
                    # TODO: cleanup any plots that don't have a corresponding socket.
        finally:
            del self.clients[websocket]
            # TODO: cleanup any plots that don't have a socket.

    async def run_source(self, websocket, data):
        """Logic for source type clients"""
        # Send the requested plot sizes
        await send(websocket, self.msg_sizes)
        msg = await websocket.recv()
        data = await get(msg)
        if data["msg_type"] == "plots":
            # data["plots"]: [{"size": [10, 12], "text": "abc"}]
            for plot in data["plots"]:
                self.plots[tuple(plot["size"])] = plot["text"]
                for client in self.clients:
                    data = {"msg_type": "plot", "text": self.plots[self.clients[client]]}
                    await send(client, data)

    async def run(self, websocket, path):
        """Server logic"""
        message = await websocket.recv()
        data = await get(message)
        if data['msg_type'] == "register":
            if data["client_type"] == "display":
                await self.run_display(websocket, data)
            elif data["client_type"] == "source":
                await self.run_source(websocket, data)

    async def serve(self):
        print(f"Running on {self.host}:{self.port}")
        await websockets.serve(self.run, self.host, self.port)

def main():
    """Setup parser"""
    parser = argparse.ArgumentParser(description="server")
    parser.add_argument("-p", "--port", help="URI", default=6789, type=int)
    args = parser.parse_args()
    # Setup display
    server = Server(args.port)
    asyncio.get_event_loop().run_until_complete(server.serve())
    asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    main()
