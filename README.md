# TradingView Alert Connector for Hyperliquid

A lightweight Python web server that receives TradingView strategy alerts and executes trades on Hyperliquid using the official Python SDK.

## Features

- **TradingView Webhook Integration**: Receives JSON alerts from TradingView strategies
- **Hyperliquid Python SDK**: Uses official Hyperliquid SDK for reliable trading
- **Percentage-based Sizing**: Supports `sizeByLeverage` for dynamic position sizing
- **Flask Web Server**: Lightweight and fast Python web framework
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
```

### 2. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt
```

### 3. Start the Server

```bash
# Development
python app.py

# Production
python start.py

# Or with Gunicorn (recommended for production)
gunicorn app:app --bind 0.0.0.0:3000
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

## Python Architecture

The connector is built entirely in Python:

1. **Flask Web Server**: Handles HTTP requests and TradingView webhooks
2. **Hyperliquid SDK**: Direct integration with Hyperliquid exchange
3. **Alert Validation**: Comprehensive validation of TradingView alerts
4. **Order Management**: Percentage-based sizing and order execution

### Key Components

- **`app.py`**: Main Flask application with all endpoints
- **`HyperliquidTrader`**: Trading class with SDK integration
- **`validate_alert()`**: Alert validation function
- **`start.py`**: Production startup script

## Deployment on Render

1. **Connect your GitHub repository**
2. **Set environment variables** in Render dashboard:
   - `HYPERLIQUID_PRIVATE_KEY`
   - `HYPERLIQUID_LEVERAGE`
   - `PORT`
3. **Set build command**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Set start command**:
   ```bash
   gunicorn app:app --bind 0.0.0.0:$PORT
   ```
5. **Deploy automatically** on push to main branch

## Development

### File Structure

```
├── app.py                 # Main Flask application
├── start.py              # Production startup script
├── hyperliquid_trader.py # Standalone trading script (legacy)
├── requirements.txt      # Python dependencies
└── .env                 # Environment variables
```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run in development mode
python app.py

# Test endpoints
curl http://localhost:3000/
curl http://localhost:3000/accounts
```

### Testing

```bash
# Test the standalone trader script
python hyperliquid_trader.py status
python hyperliquid_trader.py equity
```

## License

MIT
