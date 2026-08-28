const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const path = require('path');
const dotenv = require('dotenv');
const Simulator = require('./simulator');
const Adapter1xBet = require('./adapter/1xbet');

dotenv.config();

const app = express();
const server = http.createServer(app);
const io = new Server(server);

const PORT = process.env.PORT || 3000;

app.use(express.static(path.join(__dirname, 'public')));
app.use(express.json());

// simple API to control simulator/adapter
app.post('/api/simulator/start', (req, res) => {
  simulator.start();
  res.json({ok:true});
});
app.post('/api/simulator/stop', (req, res) => {
  simulator.stop();
  res.json({ok:true});
});

app.post('/api/adapter/1xbet/start', async (req, res) => {
  const opts = req.body || {};
  try {
    await adapter.start(opts);
    res.json({ok:true});
  } catch (e) {
    console.error(e);
    res.status(500).json({ok:false,error:e.message});
  }
});

app.post('/api/adapter/1xbet/stop', async (req, res) => {
  try {
    await adapter.stop();
    res.json({ok:true});
  } catch (e) {
    console.error(e);
    res.status(500).json({ok:false,error:e.message});
  }
});

io.on('connection', (socket) => {
  console.log('client connected');
});

server.listen(PORT, () => {
  console.log(`Server listening on http://localhost:${PORT}`);
});

// create simulator and adapter instances
const simulator = new Simulator(io);
const adapter = new Adapter1xBet(io, { simulator });

// Start simulator automatically if configured
const START_MODE = process.env.START_MODE || 'simulate';
if (START_MODE === 'simulate') {
  simulator.start();
}
