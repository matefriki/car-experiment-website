const express = require('express');
const app = express();

const http = require('http');
const server = http.createServer(app);

const { Server } = require("socket.io");
const io = new Server(server);

const fs = require('fs');
const { spawn } = require('child_process');
const e = require('express');

function getPrismPath() {
  var path = process.cwd();
  var buffer = fs.readFileSync(path + "/config.txt");
  return buffer.toString()
}

app.get('/', (req, res) => {
  res.sendFile(__dirname + '/index.html');
});

let accessible_files = ["dropdown.js", "dropdown.css", "script.js", "style.css", "person.png", "car.png", "scene.png", "handle.png", "socket.io/socket.io.js", "fonts/Barlow-SemiBold.ttf"];
accessible_files.map((file_name) => {
  app.get(`/${file_name}`, (req, res) => {
    res.sendFile(__dirname + `/${file_name}`);
  });
});

let queue = [];
let running = false;

io.on('connection', (socket) => {
  console.log('a user connected');
  socket.on('generate', (strat_name, path_length, person_x, person_y, car_x, car_y, top_corner_x, top_corner_y, bottom_corner_x, bottom_corner_y) => {
    queue.push((closed) => {
      const runner = spawn('python3', ['prism_runner.py'], { timeout: 5000 });
      runner.stdin.write(`${strat_name} ${path_length} ${person_x} ${person_y} ${car_x} ${car_y} ${top_corner_x} ${top_corner_y} ${bottom_corner_x} ${bottom_corner_y}`);
      runner.stdin.end();

      // Must have buffer because chunk size from python is smaller than full path (over path_length of 100)
      let buffer = "";
      runner.stdout.on('data', (data) => {
        buffer += data.toString();
        console.log("data");
      });

      runner.on('close', () => {
        socket.emit("path", buffer);
        console.log('close');
        closed();
      });
    });

    handleQueue();
  });
});

function handleQueue() {
  if(queue.length == 0 || running) return;
  console.log(`Handling queue, length: ${queue.length}`);
  running = true;
  let currRequest = queue.shift();
  currRequest(() => {
    running = false;
    handleQueue();
  });
}

server.listen(8000, () => {
  console.log('listening on *:8000');
});