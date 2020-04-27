import random
import websockets

from . import helpers
from . import plots

class Server:
    """A server class"""
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
        await helpers.send(websocket, data)

    async def run_display(self, websocket, data):
        """Logic for display type clients"""
        # First register them
        self.clients[websocket] = tuple(data["size"])
        print(f"Registered {websocket.remote_address[0]}:{websocket.remote_address[1]} {self.clients[websocket]}")
        await self.send_plot(websocket)
        try:
            async for message in websocket:
                # Then wait for resizes
                data = await helpers.get(message)
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
        await helpers.send(websocket, self.msg_sizes)
        msg = await websocket.recv()
        data = await helpers.get(msg)
        if data["msg_type"] == "plots":
            # data["plots"]: [{"size": [10, 12], "text": "abc"}]
            for plot in data["plots"]:
                self.plots[tuple(plot["size"])] = plot["text"]
                for client in self.clients:
                    data = {"msg_type": "plot", "text": self.plots[self.clients[client]]}
                    await helpers.send(client, data)

    async def run(self, websocket, path):
        """Server logic"""
        message = await websocket.recv()
        data = await helpers.get(message)
        if data['msg_type'] == "register":
            if data["client_type"] == "display":
                await self.run_display(websocket, data)
            elif data["client_type"] == "source":
                await self.run_source(websocket, data)

    async def serve(self):
        print(f"Running on {self.host}:{self.port}")
        await websockets.serve(self.run, self.host, self.port)

class Monitor:
    """A simple monitor. Prints messages received, randomly resizes self after messages."""
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
            await helpers.send(socket, self.msg_register)
            async for message in socket:
                data = await helpers.get(message)
                if random.random() > 0.5:
                    self.get_size()
                    await helpers.send(socket, self.msg_update)

class Source:
    """Source client. Sends a given matplotlib figure"""
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
            self.plots[tuple(size)] = plots.save_plot(self.fig, self.dpi, actual_size)

    async def run(self):
        """Client logic"""
        async with websockets.connect(self.uri) as socket:
            # Register client
            await helpers.send(socket, self.msg_register)
            message = await socket.recv()
            data = await helpers.get(message)
            if data["msg_type"] == "sizes":
                self.get_figures(data["sizes"])
                await helpers.send(socket, self.msg_plots)

