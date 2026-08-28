# Aviator Bot Server

A Python-based server for the Aviator betting bot with support for 1xBet integration.

## Features

- **Simulate Mode**: Test betting logic without live connections
- **Live Mode**: Connect to 1xBet and place real bets
- **Dry Run**: Execute live mode without actually placing bets
- **Headless/Headful Browser**: Run browser with or without UI
- **REST API**: FastAPI endpoints for all operations

## Setup

### 1. Install Dependencies

```bash
cd server
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Edit `.env`:

```env
START_MODE=simulate        # simulate or live
LIVE=false                 # Enable live mode
DRY_RUN=true              # Don't place real bets
HEADFUL=false             # Run browser headless
ONE_XBET_URL=https://1xbet.com/aviator
LOGIN_USERNAME=your_username
LOGIN_PASSWORD=your_password
```

## Running the Server

### Simulate Mode (Default)

```bash
python app.py
```

Server runs at `http://localhost:8000`

### Live Mode

```bash
START_MODE=live LIVE=true python app.py
```

**Warning**: Only enable `LIVE=true` if you want real betting. Use `DRY_RUN=true` to test live mode safely.

## API Endpoints

### Health & Config

- `GET /` - Server info
- `GET /health` - Health check
- `GET /config` - Current configuration

### Adapter Management

- `POST /api/adapter/1xbet/connect?live=false` - Connect to 1xBet
- `POST /api/adapter/1xbet/disconnect` - Disconnect
- `GET /api/adapter/1xbet/balance` - Get balance
- `GET /api/adapter/1xbet/bets` - Get active bets

### Betting

- `POST /api/adapter/1xbet/place-bet?amount=10&multiplier=2.5` - Place bet
- `POST /api/adapter/1xbet/cashout?bet_id=SIM-1` - Cash out bet

## Example Usage

```bash
# Start server
python app.py

# In another terminal:

# Connect adapter
curl -X POST http://localhost:8000/api/adapter/1xbet/connect

# Place a bet
curl -X POST "http://localhost:8000/api/adapter/1xbet/place-bet?amount=100&multiplier=2.5"

# Get balance
curl http://localhost:8000/api/adapter/1xbet/balance

# Get active bets
curl http://localhost:8000/api/adapter/1xbet/bets

# Cash out
curl -X POST "http://localhost:8000/api/adapter/1xbet/cashout?bet_id=SIM-1"
```

## Project Structure

```
server/
├── .env.example           # Environment variables template
├── config.py              # Configuration management
├── app.py                 # Main FastAPI application
├── requirements.txt       # Python dependencies
├── adapters/
│   ├── __init__.py
│   ├── base_adapter.py    # Abstract base adapter
│   └── onexbet_adapter.py # 1xBet adapter implementation
└── README.md
```

## Modes Explained

### Simulate Mode
- No actual connections made
- Bets are simulated with random outcomes
- Perfect for testing and development
- No credentials needed

### Live Mode
- Actually connects to 1xBet
- Places real bets on Aviator game
- Requires valid credentials
- Can be protected with `DRY_RUN=true`

### Dry Run
- Enables live connections but doesn't place bets
- Safe way to test live mode without money risk
- Works in conjunction with `LIVE=true`

## Development

### Adding a New Adapter

1. Create new adapter class inheriting from `BaseAdapter`
2. Implement required methods: `connect`, `disconnect`, `place_bet`, `get_balance`, `cash_out`
3. Register in adapters package
4. Add endpoints to `app.py`

### Testing

```bash
# Run with simulate mode
START_MODE=simulate python app.py

# Make requests to test endpoints
```

## License

MIT
