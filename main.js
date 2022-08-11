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

app.get('/info', (req, res) => {
  res.send('Crosswalk');
});

app.get('/', (req, res) => {
  res.sendFile(__dirname + '/index.html');
});

let accessible_files = ["script.js", "style.css", "person.png", "car.png", "scene.png", "handle.png", "socket.io/socket.io.js", "fonts/Barlow-SemiBold.ttf"];
accessible_files.map((file_name) => {
  app.get(`/${file_name}`, (req, res) => {
    res.sendFile(__dirname + `/${file_name}`);
  });
});

let queue = [];
let running = false;

io.on('connection', (socket) => {
  console.log('a user connected');
  socket.on('generate', (path_length, person_x, person_y, car_x, car_y, top_corner_x, top_corner_y, bottom_corner_x, bottom_corner_y) => {
    queue.push((closed) => {
    
    	console.log('get input parameters: ', path_length, person_x, person_y, car_x, car_y, top_corner_x, top_corner_y, bottom_corner_x, bottom_corner_y)
    	
      const runner = spawn('python3', [`${__dirname}/prism_runner.py`], { 
        timeout: 5000 
      });

      
      runner.on('error', (err) => {
				console.error(`prism runner: failed to start with error code ${err}`);
			});
			
			console.log('prism runner: started');
      console.log(`arguments for runner stdin are: ${path_length} ${person_x} ${person_y} ${car_x} ${car_y} ${top_corner_x} ${top_corner_y} ${bottom_corner_x} ${bottom_corner_y}`);
      
      runner.stdin.write(`${path_length} ${person_x} ${person_y} ${car_x} ${car_y} ${top_corner_x} ${top_corner_y} ${bottom_corner_x} ${bottom_corner_y}`);
      runner.stdin.end();

      // Must have buffer because chunk size from python is smaller than full path (over path_length of 100)
      let buffer = "";    
       
      runner.stdout.setEncoding('utf8');
      runner.stdout.on('data', (data) => {
        console.log(`prism runner: write data from stdout to buffer`);
        buffer += data.toString();
      });
      
			runner.stderr.setEncoding('utf8');
			runner.stderr.on('data', (data) => {
					console.log(`stderr: ${data}`);
					buffer += data.toString();
			});

      runner.on('close', (code) => {
        socket.emit("path", buffer);
        console.log(`prism runner: closed with code ${code}`);
        closed();
      });
      
      runner.on('exit', (code) => {
				console.log(`prism runner: exited with code ${code}`);
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
