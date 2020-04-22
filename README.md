# About

This is a websockets based plot-display thingy.

# Goals

## What this should do:

- Server-side software with two interfaces: Websocket for receiving plots, some other interface for giving plots to.
- Client-side software (could just be a html?): Receive plot from websocket.
- Matplotlib backend: Plot the figure as svg, give to interface.
- Julia integration via matplotlib?
- Plotly interface?

## Initial version (proof of concept) goals

- Only allow SVG for now

### Server-side software

- For simplicity one interface will be present that allows both putting and getting data.
- Receive/Provide plot through ws1

### Client-side software

- A html with some javascript to replace old plot with new plot.

### Matplotlib

- ???


