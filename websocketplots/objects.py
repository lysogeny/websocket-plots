import json
import random

import websockets

from . import plots

class AbstractBase:
    """Base class for all websocket utilising classes"""
    def __init__(self, verbose):
        self.verbose = verbose

    async def get(self, msg) -> dict:
        """Print message if verbose and load contents"""
        if self.verbose:
            print(f"> {msg}")
        return json.loads(msg)

    async def send(self, socket, data: dict):
        """JSON format message and print message if verbose"""
        msg = json.dumps(data)
        if self.verbose:
            print(f"< {msg}")
        await socket.send(msg)

    async def run(self, websocket, path):
        """Websocket handler"""
        raise NotImplementedError

class AbstractServer(AbstractBase):
    """Server base class. Additionally provides `serve` method for serving server"""
    def __init__(self, port, host, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.port = port
        self.host = host

    async def serve(self):
        """Server running coroutive"""
        if self.verbose:
            print(f"Running on {self.host}:{self.port}")
        await websockets.serve(self.run, self.host, self.port)

class AbstractClient(AbstractBase):
    """Client baseclass. Additionally needs to define a URI to listen on"""
    def __init__(self, uri, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.uri = uri

    @property
    def msg_register(self):
        """Message to register on server"""
        raise NotImplementedError

    async def client_logic(self, socket):
        """Logic for client"""
        raise NotImplementedError

    async def run(self):
        """Client socket run. Register with server and delegate to `client_logic`"""
        async with websockets.connect(self.uri) as socket:
            # Register client
            await self.send(socket, self.msg_register)
            await self.client_logic(socket)


class Server(AbstractServer):
    """A server class"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.clients = dict()
        # {client: (w, h)}
        self.plots = dict()
        # {(w, h): str}

    @property
    def msg_sizes(self):
        return {"msg_type": "sizes", "sizes": list(set(self.clients.values()))}

    async def send_plot(self, websocket):
        """Send plots to participants"""
        if self.clients[websocket] not in self.plots:
            # If there is no plot we can't just magic it out of thin air.
            # Thus I just make some empty SVG tags.
            self.plots[self.clients[websocket]] = "<SVG></SVG>"
        data = {"msg_type": "plot", "text": self.plots[self.clients[websocket]]}
        await self.send(websocket, data)

    async def run_display(self, websocket, data):
        """Logic for display type clients"""
        # First register them
        self.clients[websocket] = tuple(data["size"])
        print(f"Registered {websocket.remote_address[0]}:{websocket.remote_address[1]} {self.clients[websocket]}")
        await self.send_plot(websocket)
        try:
            async for message in websocket:
                # Then wait for resizes
                data = await self.get(message)
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
        await self.send(websocket, self.msg_sizes)
        msg = await websocket.recv()
        data = await self.get(msg)
        if data["msg_type"] == "plots":
            # data["plots"]: [{"size": [10, 12, 1], "text": "abc"}]
            for plot in data["plots"]:
                self.plots[tuple(plot["size"])] = plot["text"]
                for client in self.clients:
                    data = {"msg_type": "plot", "text": self.plots[self.clients[client]]}
                    await self.send(client, data)

    async def run(self, websocket, path):
        """Server logic"""
        message = await websocket.recv()
        data = await self.get(message)
        if data['msg_type'] == "register":
            if data["client_type"] == "display":
                await self.run_display(websocket, data)
            elif data["client_type"] == "source":
                await self.run_source(websocket, data)

class Monitor(AbstractClient):
    """A simple monitor. Prints messages received, randomly resizes self after messages."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.get_size()

    @property
    def msg_register(self):
        """Message to register on server"""
        return {"msg_type": "register",
                "client_type": "display",
                "size": self.size}
    @property
    def msg_update(self):
        """Message to update status on server"""
        return {"msg_type": "update",
                "size": self.size}

    def get_size(self):
        """Gets own random size"""
        self.size = tuple(random.randrange(0, 1000) for i in range(0, 2)) + (random.randRange(1, 3),)

    async def client_logic(self, socket):
        """awaits messages and randomly resizes"""
        async for message in socket:
            data = await self.get(message)
            if random.random() > 0.5:
                self.get_size()
                await self.send(socket, self.msg_update)


class Source(AbstractClient):
    """Source client. Sends a given matplotlib figure"""
    def __init__(self, fig, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fig = fig
        self.sizes = [] # tuples
        self.plots = {} # {(w, h, d): str}

    @property
    def msg_register(self):
        """Message to register on server"""
        return {"msg_type": "register", "client_type": "source"}

    @property
    def msg_plots(self):
        """Message to send plots to server"""
        return {
            "msg_type": "plots",
            "plots": [
                {"size": i, "text": self.plots[i]} for i in self.plots
            ]
        }

    def get_figures(self, sizes: list):
        """Gets plots at given sizes"""
        for size in sizes:
            pixels = size[0:2]
            dpi = size[2] * 96
            inches = tuple(i/dpi for i in pixels)
            self.plots[tuple(size)] = plots.save_plot(self.fig, dpi, inches)

    async def client_logic(self, socket):
        """Waits for server to tell us sizes, then creates plots and responds"""
        message = await socket.recv()
        data = await self.get(message)
        if data["msg_type"] == "sizes":
            self.get_figures(data["sizes"])
            await self.send(socket, self.msg_plots)

class ConstSource(AbstractClient):
    """Source client. Sends a given matplotlib figure"""
    def __init__(self, txt, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.txt = txt
        self.sizes = set() # {(w, h): str}kjb

    @property
    def msg_register(self):
        """Message to register on server"""
        return {"msg_type": "register", "client_type": "source"}

    @property
    def msg_plots(self):
        """Message to send plot to server"""
        return {
            "msg_type": "plots",
            "plots": [
                {"size": i, "text": self.txt} for i in self.sizes
            ]
        }

    async def client_logic(self, socket):
        """Waits for server to tell us sizes, then sends plot"""
        message = await socket.recv()
        data = await self.get(message)
        if data["msg_type"] == "sizes":
            for size in data['sizes']:
                self.sizes.add(tuple(size))
            await self.send(socket, self.msg_plots)

