# About

This is a websockets based plot-distribution thingy.

## Motivation

This exists for people who work on remote machines over SSH, and don't want to
use X11-forwarding (which can be quite slow and prone to breaking) for plot
display.

## Function

This software provides a couple of files to run a plot-distribution server that
runs through websockets.

The (display) client registers with the server by sending it's size. Another type of
client (here called source) can then ask the server for sizes it needs and
produce adequate SVG plots which it then sends to the server. The server then
distributes these SVGs to the display clients.

The `wsp-server` executable can be used to run such a server, see it's help
page for info on how to use it. A sample client is included in the form of an
`.html` file.
A sample script `wsp-random` sends a sample plot to the server.

## Caveats

- Currently there is no authentication or other mechanism to prohibit
  unauthorised communication. Consider setting this up behind
  an http reverse proxy with some form of authentication.
- Currently both types of communications (sending and receiving) take place
  over the same socket. If you run this without authentication anyone with
  access to your network can send plots (and potentially harmful things) to the
  server, and through that to your browser. Consider only running this in
  a secure network.

## Todos

- Figure out how to make this a matplotlib backend.
- Change sending of plots to a different socket to disallow unauthorised access.
- Figure out how to use this with plotly
- Qt5 client.
- Persistent sources. Possibility to respond to resize events?

## Similar projects

Matplotlib has has the backend `webagg`, which also provides plots over the
web, but is unsuitable for my uses because: 

- No indication of where the plot is being hosted. The backend tries to open
  a browser, which doesn't make sense for headless machines.
- The backend blocks the REPL
