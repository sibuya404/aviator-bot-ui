// Simple Aviator simulator that emits round events via socket.io
// This is for safe local testing. Each round has an id, start timestamp, and crash multiplier.

class Simulator {
  constructor(io) {
    this.io = io;
    this.interval = null;
    this.roundIndex = 0;
    this.running = false;
    this.roundDurationMs = 8000; // 8s rounds
  }

  start() {
    if (this.running) return;
    this.running = true;
    this._nextRound();
    console.log('Simulator started');
  }

  stop() {
    this.running = false;
    if (this.interval) clearTimeout(this.interval);
    console.log('Simulator stopped');
  }

  _nextRound() {
    if (!this.running) return;
    const id = ++this.roundIndex;
    const startAt = Date.now();
    const countdown = 3000; // announce roundStart 3s before

    // announce upcoming round
    this.io.emit('roundUpcoming', { id, startAt: startAt + countdown });

    setTimeout(() => {
      this.io.emit('roundStart', { id, startAt: Date.now() });

      // simulate a crash multiplier between 1.00 and 10.00 with heavy bias toward low values
      const r = Math.random();
      const multiplier = Math.max(1.0, Math.round((1 + Math.pow(r, 3) * 9) * 100) / 100);

      setTimeout(() => {
        this.io.emit('roundCrash', { id, multiplier });
        // schedule next round
        this.interval = setTimeout(() => this._nextRound(), 1000);
      }, this.roundDurationMs - countdown);
    }, countdown);
  }
}

module.exports = Simulator;
