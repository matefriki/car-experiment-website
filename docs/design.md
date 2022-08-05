# Design choices
In terms of the number of different frameworks used, both on the client and server side, the car-experiment-website is actually rather simple. 

## The server
Starting first with the web server, there are really only two important external libraries being used. The first is `express`, a library for easily serving static HTML content. It is used to serve everything from the page itself, to its associated js/css/image files. The second is `socket.io`, a library that provides a simple interface to the websocket protocol, as well as robust backwards compatibility. Websockets are what the client and server use to communicate with each other after the initial page has been served.

## The client
The client side has almost as few moving parts. First off, it uses the client part of the `socket.io` module for communicating with the server. For the actual graphics, namely the world visualization, the `PixiJS` javascript game engine is used. This library makes it easy to draw image sprites on the HTML canvas and move them around. Other than that, everything is done in pure HTML/CSS/JS, though for the dropdown input a custom JS library is used.

## Websocket communication
As previously mentioned, the client and server use websockets to communicate with each other. The websocket protocol is asynchronous, unlike the initial page request which returns 
the HTML, and its associated scripts, images, etc. 

### Background
When a user tries to access the webpage, their web browser sends a HTTP GET request to the server. The server receives this request and interprets it, eventually sending the HTML page back to the user. Once the user's browser receives a response from the server (containing the page content) the connection to the server is closed, meaning that no further communication can be made between the two. What happens with websockets instead is that a connection to the server is constantly kept open, as long as the user remains on the page. This connection is entirely separate from the one made to the server to request the page, and happens through a different port. Once this connection has been established, the client and the server are free to send messages to each other asynchronously. This means that both the client and the server don't have to wait for each other before sending and receiving data, or handling their other tasks. For instance, the client could send multiple messages at once without a response, and the server would just handle them when it was ready. 

### Websocket events
In order to receive data from each other, both client and server must register to listen for message events from the other party. These message events each have an associated label, that was previously agreed upon, which describes what the event relates to. For example, say we had created a simple chat application, where the client has a text box where they can input some text to send to the server. The client might send this data (the text message) with the label *"send"*, or *"message"*, anything that describes what action is occurring. The server would then be listening for *"send"* events on the websocket, and would handle the event and process the user's text.

### The API
In the car experiment application there are three websocket labels currently in use, for the three main actions that can occur between client and server. First, and most important, is the *"generate"* message which is sent by the client when the user clicks the generate button, and includes all the starting state settings as its payload. This is the only message sent by the client, as at that point control is handed over to the server. In addition to listening for the *"generate"* message, the server sends two messages of its own in response. The first is the *"path"* message, which includes as its data the trace generated from the user's input in JSON format. The second is the *"graph"* message, which sends over the probability graph that is also generate from the user's input, to be displayed by the website.