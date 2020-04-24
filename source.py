#!/usr/bin/env python3

"""A source client that sends something. Useful for testing procedures"""

import io
import json
import asyncio
import websockets
import random
import argparse
import matplotlib as mpl
import matplotlib.pyplot as plt

def random_plot():
    """Plots random numbers"""
    #size_actual = [s/dpi for s in size]
    indexes = list(range(0, 100))
    rand = [random.random() for i in indexes]
    fig = plt.figure()
    plt.plot(indexes, rand)
    return fig

def save_plot(fig, dpi, size):
    data = io.StringIO()
    fig.set_size_inches(*size)
    fig.savefig(data, format='svg', dpi=dpi)#, figsize=size)
    data.seek(0)
    return data.read()

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

class Source:
    """Source client"""
    def __init__(self, uri, fig, dpi=300):
        self.uri = uri
        self.dpi = dpi
        self.fig = fig
        self.sizes = [] # tuples
        self.plots = {} # {(w, h): str}

    @property
    def msg_register(self):
        return {"msg_type": "register", "client_type": "source"}

    @property
    def msg_plots(self):
        return {
            "msg_type": "plots",
            "plots": [
                {"size": i, "text": self.plots[i]} for i in self.plots
            ]
        }

    def get_figures(self, sizes):
        """Gets plots at given sizes"""
        for size in sizes:
            actual_size = tuple(i/self.dpi for i in size)
            print(actual_size)
            self.plots[tuple(size)] = save_plot(self.fig, self.dpi, actual_size)

    async def run(self):
        """Client logic"""
        async with websockets.connect(self.uri) as socket:
            # Register client
            await send(socket, self.msg_register)
            message = await socket.recv()
            data = await get(message)
            if data["msg_type"] == "sizes":
                self.get_figures(data["sizes"])
                await send(socket, self.msg_plots)


def main():
    """Setup parser"""
    parser = argparse.ArgumentParser(description="source client")
    parser.add_argument("-u", "--uri", help="URI", default="ws://localhost:6789")
    parser.add_argument("-d", "--dpi", help="DPI", default=72, type=int)
    args = parser.parse_args()
    # Setup display
    fig = random_plot()
    source = Source(args.uri, fig, args.dpi)
    asyncio.get_event_loop().run_until_complete(source.run())

if __name__ == "__main__":
    main()
