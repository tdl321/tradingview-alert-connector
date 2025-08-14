# TradingView Alert Connector for Hyperliquid

A lightweight webhook server that receives TradingView strategy alerts and executes trades on Hyperliquid using the official Python SDK.

## Architecture

This connector uses a **hybrid approach**:
- **TypeScript/Node.js**: Web server, TradingView webhook handling, and API endpoints
- **Python**: Hyperliquid SDK integration for trading operations

## Features

- **TradingView Webhook Integration**: Receives JSON alerts from TradingView strategies
- **Hyperliquid Python SDK**: Uses official Hyperliquid SDK for reliable trading
- **Percentage-based Sizing**: Supports `sizeByLeverage` for dynamic position sizing
- **Render Deployment**: Optimized for hosting on Render
- **Health Checks**: Built-in endpoints for monitoring

## Quick Start

### 1. Environment Variables

Create a `.env` file with your Hyperliquid credentials:

```env
HYPERLIQUID_PRIVATE_KEY=your_private_key_here
HYPERLIQUID_LEVERAGE=5
NODE_ENV=production
PORT=3000
PYTHON_PATH=python  # or path to your Python executable
```

### 2. Install Dependencies

```bash
# Install Node.js dependencies
npm install

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Start the Server

```bash
# Development
npm run dev

# Production
npm start
```

## TradingView Alert Format

Send POST requests to `/` with this JSON format:

```json
{
  "exchange": "hyperliquid",
  "strategy": "my_strategy",
  "market": "BTC",
  "sizeByLeverage": 0.2,
  "order": "buy",
  "price": 45000,
  "position": "long",
  "reverse": false,
  "passphrase": "your_passphrase"
}
```

### Alert Fields

- `exchange`: Must be "hyperliquid"
- `strategy`: Your strategy name
- `market`: Trading pair (e.g., "BTC", "ETH")
- `sizeByLeverage`: Percentage of equity (0.2 = 20%)
- `order`: "buy" or "sell"
- `price`: Current market price
- `position`: "long" or "short"
- `reverse`: Boolean for reverse orders
- `passphrase`: Security passphrase

## API Endpoints

- `GET /` - Health check
- `GET /accounts` - Account status
- `POST /` - TradingView webhook (main endpoint)

## Python Integration

The connector uses a Python script (`hyperliquid_trader.py`) that:

1. **Initializes Hyperliquid SDK** with your private key
2. **Handles account operations** (status, equity, balance)
3. **Executes trades** based on TradingView alerts
4. **Supports percentage-based sizing** with `sizeByLeverage`

### Testing Python Script

```bash
# Check account status
python hyperliquid_trader.py status

# Get account equity
python hyperliquid_trader.py equity

# Place an order (example)
python hyperliquid_trader.py order '{"market":"BTC","order":"buy","price":45000,"sizeByLeverage":0.2}'
```

## Deployment on Render

1. **Connect your GitHub repository**
2. **Set environment variables** in Render dashboard:
   - `HYPERLIQUID_PRIVATE_KEY`
   - `HYPERLIQUID_LEVERAGE`
   - `PYTHON_PATH`
3. **Install Python dependencies** in build command:
   ```bash
   pip install -r requirements.txt
   ```
4. **Deploy automatically** on push to main branch

## Development

### File Structure

```
├── src/                    # TypeScript source code
│   ├── controllers/        # Express routes
│   ├── services/          # Business logic
│   └── index.ts           # Main server file
├── hyperliquid_trader.py  # Python trading script
├── requirements.txt       # Python dependencies
└── package.json          # Node.js dependencies
```

### Adding New Features

- **TypeScript**: Add new endpoints in `src/controllers/`
- **Python**: Extend `hyperliquid_trader.py` with new trading functions

## License

MIT
