var osc = require("osc"),
    http = require("http"),
    WebSocket = require("ws");

// Create an Express server app
// and serve up a directory of static files.

// Listen for Web Socket requests.

// Listen for Web Socket connections.
var inport, oscMin, sock, udp;

oscMin = require('osc-min');

udp = require("dgram");

if (process.argv[2] != null) {
  inport = parseInt(process.argv[2]);
} else {
  inport = 57121;
}

console.log("OSC listener running at http://localhost:" + inport);

var express = require('express')
var app = express();
var server = app.listen(8081);
var wss = new WebSocket.Server({
    server: server
});

//~verbatim:examples[0]~
//### A simple OSC printer;
wss.on("connection", function (socket) {
    var socketPort = new osc.WebSocketPort({
        socket: socket
    });

    socketPort.on("message", function (oscMsg) {
        console.log("An OSC Message was received!", oscMsg);
    });
});

sock = udp.createSocket("udp4", function(msg, rinfo) {
  var error;
  try {
    const message = oscMin.fromBuffer(msg);
    const element = message.elements[0];
    return console.log(element);
  } catch (error1) {
    error = error1;
    return console.log("invalid OSC packet");
  }
});

sock.bind(inport, '192.168.129.160');
