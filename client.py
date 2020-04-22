#!/usr/bin/env python3

"""Websockets based plot distribution proof of concept server software"""

import json
import asyncio
import websockets
import random

async def receiver(uri):
    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            if 'data' in data:
                print(f"Received: {data}")

async def sender(uri):
    async with websockets.connect(uri) as websocket:
        message = json.dumps({"data":random.random()})
        await websocket.send(message)

def main():
    #asyncio.get_event_loop().run_until_complete(sender("ws://localhost:6666"))
    asyncio.get_event_loop().run_until_complete(receiver("ws://localhost:6789"))
    #asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    main()
