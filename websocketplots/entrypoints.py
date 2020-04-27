import asyncio
import websockets
import argparse

from . import objects
from . import plots

def server():
    """Server entrypoint"""
    parser = argparse.ArgumentParser(description="Websocketplots server")
    parser.add_argument("-p", "--port", help="port to listen on", default=6789, type=int)
    args = parser.parse_args()
    # Setup display
    server = objects.Server(args.port)
    asyncio.get_event_loop().run_until_complete(server.serve())
    asyncio.get_event_loop().run_forever()

def monitor():
    """Monitor entrypoint"""
    parser = argparse.ArgumentParser(description="Dumb display client")
    parser.add_argument("-u", "--uri", help="URI of websocket", default="ws://localhost:6789")
    args = parser.parse_args()
    # Setup display
    display = objects.Monitor(args.uri)
    asyncio.get_event_loop().run_until_complete(display.run())
    asyncio.get_event_loop().run_forever()

def random():
    """Random plot entrypoint"""
    parser = argparse.ArgumentParser(description="Random plot source client")
    parser.add_argument("-u", "--uri", help="URI", default="ws://localhost:6789")
    parser.add_argument("-d", "--dpi", help="DPI", default=96, type=int)
    args = parser.parse_args()
    # Create a random plot
    fig = plots.random_plot()
    # Setup display
    source = objects.Source(args.uri, fig, args.dpi)
    asyncio.get_event_loop().run_until_complete(source.run())
