#!/usr/bin/env python3

"""Websockets based plot distribution proof of concept server software"""

import json
import asyncio
import random
import io
import websockets
import matplotlib as mpl
import matplotlib.pyplot as plt

def random_plot():
    indexes = list(range(0, 100))
    rand = [random.random() for i in indexes]
    fig = plt.figure()
    plt.plot(indexes, rand)
    data = io.StringIO()
    fig.savefig(data, format='svg')
    data.seek(0)
    return data.read()


async def sender(uri):
    plot = random_plot()
    async with websockets.connect(uri) as websocket:
        message = json.dumps({"data": plot})
        await websocket.send(message)

def main():
    asyncio.get_event_loop().run_until_complete(sender("ws://localhost:6789"))
    #asyncio.get_event_loop().run_until_complete(receiver("ws://localhost:6666"))
    #asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    main()
