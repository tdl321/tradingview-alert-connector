# TradingView Alert Connector for Hyperliquid

A lightweight webhook server that receives TradingView strategy alerts and executes trades on Hyperliquid.

## Features

- **TradingView Webhook Integration**: Receives JSON alerts from TradingView strategies
- **Hyperliquid Trading**: Executes trades using the Hyperliquid SDK
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
```

### 2. Install Dependencies

```bash
npm install
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

## Deployment on Render

1. Connect your GitHub repository
2. Set environment variables in Render dashboard
3. Deploy automatically on push to main branch

## License

MIT
