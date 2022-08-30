const express = require('express');
const app = express();

const http = require('http');
const server = http.createServer(app);
const { Server } = require("socket.io");
const io = new Server(server);
const PIXI = require('pixi.js');


const fs = require('fs');
const { spawn } = require('child_process');
const e = require('express');

function getPrismPath() {
  var path = process.cwd();
  var buffer = fs.readFileSync(__dirname + "/config.txt");
  return buffer.toString()
}

app.set('view engine', 'ejs');

app.use('/js', express.static(__dirname + '/node_modules/bootstrap/dist/js'));
app.use('/css', express.static(__dirname + '/node_modules/bootstrap/dist/css'));
app.use('/pixi', express.static(__dirname + '/node_modules/pixi.js/dist/cjs'));
app.use('/socket.io', express.static(__dirname + '/node_modules/socket.io/client-dist'));
app.use('/assets', express.static(__dirname + '/assets'));
app.use('/public', express.static(__dirname + '/public'));
app.use('/source', express.static(__dirname + '/source'));
app.use('/fonts', express.static(__dirname + '/fonts'));
app.use('/', express.static(__dirname + '/'));


app.get('/', (req, res) => {
  res.render(__dirname + '/pages/index.ejs');
});

app.get('/about', (req, res) => {
  res.render(__dirname + '/pages/about.ejs');
});

app.get('/app', (req, res) => {
  res.render(__dirname + '/pages/app.ejs');
});

app.get('/code', (req, res) => {
  res.render(__dirname + '/pages/code.ejs');
});

app.get('/paper', (req, res) => {
  res.render(__dirname + '/pages/paper.ejs');
});

app.get('*', (req, res) => {
  res.status(404).render(__dirname + '/pages/404.ejs');
});

let accessible_files = ["assets/replay.png", "assets/spin.png", "public/js/dropdown.js", "public/css/dropdown.css", "script.js", "public/css/style.css", "assets/person.png", "assets/car.png", "assets/scene.png", "assets/handle.png", "socket.io/socket.io.js", "fonts/Barlow-SemiBold.ttf"];
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

      console.log('get input parameters: ', path_length, person_x, person_y, car_x, car_y, top_corner_x, top_corner_y, bottom_corner_x, bottom_corner_y)

      // const runner = spawn('python3', ['prism_runner.py', `${strat_name}`, `${path_length}`, `${person_x}`, `${person_y}`, `${car_x}`, `${car_y}`, `${top_corner_x}`, `${top_corner_y}`, `${bottom_corner_x}`, `${bottom_corner_y}`], { timeout: 50000 });
      const runner = spawn('python3', [__dirname + '/prism_runner.py'], { timeout: 50000 });
      runner.stdin.write(`${strat_name} ${path_length} ${person_x} ${person_y} ${car_x} ${car_y} ${top_corner_x} ${top_corner_y} ${bottom_corner_x} ${bottom_corner_y}`);
      runner.stdin.end();

      runner.on('error', (err) => {
				console.error(`prism runner: failed to start with error code ${err}`);
			});

      console.log('prism runner: started');
      console.log(`arguments for runner stdin are: ${path_length} ${person_x} ${person_y} ${car_x} ${car_y} ${top_corner_x} ${top_corner_y} ${bottom_corner_x} ${bottom_corner_y}`);

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

        // Send graph placeholders
        fs.readFile(__dirname + '/temp/graph_left.png', (err, data) => {
          console.log(`send left graph placeholder`)
          if (err) {
            console.error(err);
            return;
          }
          setTimeout(() => socket.emit("graph_left", data), 1000);
        });

        fs.readFile(__dirname + '/temp/graph_right.png', (err, data) => {
          console.log(`send right graph placeholder`)
          if (err) {
            console.error(err);
            return;
          }
          setTimeout(() => socket.emit("graph_right", data), 1000);
        });
      });

      runner.on('exit', (code) => {
				console.log(`prism runner: exited with code ${code}`);
			});
    });
    handleQueue();
  });
});

function handleQueue() {
  if (queue.length == 0 || running) return;
  console.log(`Handling queue, length: ${queue.length}`);
  running = true;
  let currRequest = queue.shift();
  currRequest(() => {
    running = false;
    handleQueue();
  });
}

app.listen(8000, () => {
  console.log('listening on *:8000');
});
