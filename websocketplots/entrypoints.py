import asyncio
import websockets
import argparse

from . import objects
from . import plots

def server():
    """Server entrypoint"""
    parser = argparse.ArgumentParser(description="Websocketplots server")
    parser.add_argument("-p", "--port", help="port to listen on", default=6789, type=int)
    parser.add_argument("-o", "--host", help="host to listen on", default="localhost")
    parser.add_argument("-v", "--verbose", help="Be verbose", default=False, action="store_true")
    args = parser.parse_args()
    # Setup display
    server = objects.Server(port=args.port, host=args.host, verbose=args.verbose)
    asyncio.get_event_loop().run_until_complete(server.serve())
    asyncio.get_event_loop().run_forever()

def monitor():
    """Monitor entrypoint"""
    parser = argparse.ArgumentParser(description="Dumb display client")
    parser.add_argument("-u", "--uri", help="URI of websocket", default="ws://localhost:6789")
    parser.add_argument("-v", "--verbose", help="Be verbose", default=False, action="store_true")
    args = parser.parse_args()
    # Setup display
    display = objects.Monitor(uri=args.uri, verbose=args.verbose)
    asyncio.get_event_loop().run_until_complete(display.run())
    asyncio.get_event_loop().run_forever()

def random():
    """Random plot entrypoint"""
    parser = argparse.ArgumentParser(description="Random plot source client")
    parser.add_argument("-u", "--uri", help="URI", default="ws://localhost:6789")
    parser.add_argument("-v", "--verbose", help="Be verbose", default=False, action="store_true")
    args = parser.parse_args()
    # Create a random plot
    fig = plots.random_plot()
    # Setup display
    source = objects.Source(uri=args.uri, fig=fig, verbose=args.verbose)
    asyncio.get_event_loop().run_until_complete(source.run())

def send():
    """Send a SVG file

    Kind of violates the protocol as it doesn't change sizes.
    """
    parser = argparse.ArgumentParser(description="SVG file plot source client")
    parser.add_argument("-u", "--uri", help="URI", default="ws://localhost:6789")
    parser.add_argument("-v", "--verbose", help="Be verbose", default=False, action="store_true")
    parser.add_argument("filename", help="URI", default="ws://localhost:6789")
    args = parser.parse_args()
    with open(args.filename, 'r') as connection:
        txt = connection.read()
    source = objects.ConstSource(uri=args.uri, txt=txt, verbose=args.verbose)
    asyncio.get_event_loop().run_until_complete(source.run())
