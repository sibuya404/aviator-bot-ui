const fs = require('fs');
const path = require('path');
const dotenv = require('dotenv');
const { chromium } = require('playwright');

dotenv.config();

class Adapter1xBet {
  constructor(io, opts = {}) {
    this.io = io;
    this.simulator = opts.simulator;
    this.browser = null;
    this.context = null;
    this.page = null;
    this.running = false;
  }

  async start(options = {}) {
    // options: { live: boolean, headful: boolean, dryRun: boolean }
    const live = options.live === true || process.env.LIVE === 'true';
    const headful = options.headful !== undefined ? options.headful : (process.env.HEADFUL !== 'false');
    const dryRun = options.dryRun !== undefined ? options.dryRun : (process.env.DRY_RUN !== 'true' ? true : true);

    this.options = { live, headful, dryRun };

    // If running in simulate-only mode, just wire events from simulator
    if (!live) {
      this._attachToSimulator();
      this.running = true;
      console.log('1xBet adapter started in simulate-only mode');
      return;
    }

    // Live mode with Playwright
    if (live) {
      if (!process.env.LIVE || process.env.LIVE !== 'true') {
        console.warn('LIVE environment variable not set to true — refusing to run live unless explicitly set. To run live set LIVE=true in your .env');
        throw new Error('Live mode requires LIVE=true in .env and explicit confirmation. Aborting.');
      }

      // Safety: ensure DRY_RUN toggle
      if (dryRun) {
        console.log('DRY_RUN enabled — adapter will not place real bets');
      }

      this.browser = await chromium.launch({ headless: !headful });
      this.context = await this.browser.newContext();
      this.page = await this.context.newPage();

      // Navigate to 1xBet Aviator page — NOTE: URL may change and site uses lots of anti-bot protections.
      const target = process.env.ONE_XBET_URL || 'https://1xbet.com/aviator';
      console.log('Navigating to', target);

      await this.page.goto(target, { waitUntil: 'domcontentloaded' });

      // You MUST login manually if site prompts. This code does NOT fill credentials automatically.
      this._listenPage();

      this.running = true;
      console.log('1xBet adapter started in live mode (dryRun=' + dryRun + ')');
    }
  }

  _attachToSimulator() {
    if (!this.simulator) return;
    // forward simulator events to UI and act on them according to strategy
    this.simulatorIo = (ev) => {
      // no-op placeholder
    };

    // we just forward simulator events to socket.io so UI can control bets
    // the server already emits simulator events; the adapter can also emit adapter-specific logs
    this.io.emit('adapterLog', { msg: 'Adapter attached to simulator (simulate-only)' });

    // Example: listen for simulator events if it exposes any event emitter (here it doesn't), so we rely on client events.
  }

  _listenPage() {
    if (!this.page) return;

    // basic console logging from page
    this.page.on('console', (msg) => {
      this.io.emit('adapterLog', { msg: '[page] ' + msg.text() });
    });

    // NOTE: site structure changes. You will need to inspect the 1xBet page and modify selectors.
    // We do not provide bypasses for captchas; if a captcha appears you must solve it manually.
  }

  async stop() {
    if (this.page) await this.page.close().catch(()=>{});
    if (this.context) await this.context.close().catch(()=>{});
    if (this.browser) await this.browser.close().catch(()=>{});
    this.running = false;
    this.io.emit('adapterLog', { msg: 'Adapter stopped' });
  }
}

module.exports = Adapter1xBet;
