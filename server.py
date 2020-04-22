#!/usr/bin/env python3

"""Websockets based plot distribution proof of concept server software"""

import json
import asyncio
import websockets

class Server:
    """Websockets plot-distribution server"""
    def __init__(self):
        self.data = "aaa"
        self.clients = set()

    @property
    def data_msg(self):
        """message of data"""
        return json.dumps({"data": self.data})

    async def send_data(self):
        """Send data to clients"""
        if self.clients:
            await asyncio.wait([client.send(self.data_msg) for client in self.clients])

    async def run(self, websocket, path):
        """The server logic"""
        self.clients.add(websocket)
        print(f"New client {websocket.remote_address[0]}:{websocket.remote_address[1]} (total: {len(self.clients)})")
        await websocket.send(self.data_msg)
        try:
            async for message in websocket:
                data = json.loads(message)
                if 'data' in data:
                    self.data = data['data']
                    print(f"Got new data from {websocket.remote_address[0]}:{websocket.remote_address[1]}")
                    await self.send_data()
        finally:
            print(f"Lost client {websocket.remote_address[0]}:{websocket.remote_address[1]}")
            self.clients.remove(websocket)

def main():
    """Parse args, run server"""
    server = Server()
    start_server = websockets.serve(server.run, "localhost", 6789)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    main()
