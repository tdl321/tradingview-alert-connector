#!/usr/bin/env python3
"""
TradingView Alert Connector for Hyperliquid
Complete Python web server for handling TradingView alerts and executing trades
"""

from flask import Flask, request, jsonify
from hyperliquid import HyperliquidSync
from eth_account import Account
import os
import json
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class HyperliquidTrader:
    def __init__(self):
        self.client = None
        self.account = None
        self.initialize_client()
    
    def initialize_client(self):
        """Initialize the Hyperliquid client"""
        try:
            private_key = os.getenv('HYPERLIQUID_PRIVATE_KEY')
            if not private_key:
                logger.error("HYPERLIQUID_PRIVATE_KEY not found in environment variables")
                return
            
            # Remove '0x' prefix if present
            if private_key.startswith('0x'):
                private_key = private_key[2:]
            
            # Create account from private key
            self.account = Account.from_key(private_key)
            
            # Initialize Hyperliquid client
            self.client = HyperliquidSync(
                wallet=self.account,
                environment="mainnet"  # or "testnet"
            )
            
            logger.info("Hyperliquid client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Hyperliquid client: {e}")
    
    def get_account_status(self) -> Dict[str, Any]:
        """Get account status and balance"""
        try:
            if not self.client:
                return {"ready": False, "error": "Client not initialized"}
            
            # Get account info
            account_info = self.client.get_account_info()
            balance = account_info.get('balance', 0)
            
            return {
                "ready": True,
                "balance": balance,
                "address": self.account.address if self.account else None
            }
            
        except Exception as e:
            logger.error(f"Error getting account status: {e}")
            return {"ready": False, "error": str(e)}
    
    def get_account_equity(self) -> float:
        """Get account equity for percentage-based sizing"""
        try:
            if not self.client:
                return 0.0
            
            # Get account info
            account_info = self.client.get_account_info()
            equity = account_info.get('equity', 0.0)
            
            logger.info(f"Account equity: {equity}")
            return equity
            
        except Exception as e:
            logger.error(f"Error getting account equity: {e}")
            return 0.0
    
    def place_order(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Place an order based on TradingView alert"""
        try:
            if not self.client:
                return {"success": False, "error": "Client not initialized"}
            
            # Extract order parameters
            market = alert_data.get('market', '').upper()
            order_type = alert_data.get('order', '').lower()
            price = float(alert_data.get('price', 0))
            
            # Calculate size
            size = self._calculate_order_size(alert_data)
            if size <= 0:
                return {"success": False, "error": "Invalid order size"}
            
            # Determine side
            side = "buy" if order_type == "buy" else "sell"
            
            # Place the order
            order_result = self.client.place_order(
                symbol=market,
                side=side,
                order_type="market",  # or "limit"
                size=size,
                price=price
            )
            
            logger.info(f"Order placed successfully: {order_result}")
            
            return {
                "success": True,
                "order_id": order_result.get('id', 'unknown'),
                "size": size,
                "side": side.upper(),
                "market": market,
                "price": price
            }
            
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return {"success": False, "error": str(e)}
    
    def _calculate_order_size(self, alert_data: Dict[str, Any]) -> float:
        """Calculate order size based on alert data"""
        try:
            # Priority: sizeByLeverage > sizeUsd > size
            if 'sizeByLeverage' in alert_data:
                equity = self.get_account_equity()
                leverage = float(alert_data['sizeByLeverage'])
                size = equity * leverage
                logger.info(f"Calculated size from leverage: {size} (equity: {equity}, leverage: {leverage})")
                return size
            
            elif 'sizeUsd' in alert_data:
                size = float(alert_data['sizeUsd'])
                logger.info(f"Using sizeUsd: {size}")
                return size
            
            elif 'size' in alert_data:
                size = float(alert_data['size'])
                logger.info(f"Using size: {size}")
                return size
            
            else:
                logger.error("No size specified in alert data")
                return 0.0
                
        except Exception as e:
            logger.error(f"Error calculating order size: {e}")
            return 0.0

def validate_alert(alert_data: Dict[str, Any]) -> bool:
    """Validate TradingView alert data"""
    try:
        # Basic validation
        if not alert_data:
            logger.error('Alert message is empty')
            return False

        # Check required fields
        required_fields = ['exchange', 'strategy', 'market', 'order', 'price']
        for field in required_fields:
            if not alert_data.get(field):
                logger.error(f'Missing required field: {field}')
                return False

        # Validate exchange
        if alert_data['exchange'].lower() != 'hyperliquid':
            logger.error(f'Unsupported exchange: {alert_data["exchange"]}')
            return False

        # Validate order type
        if alert_data['order'].lower() not in ['buy', 'sell']:
            logger.error(f'Invalid order type: {alert_data["order"]}')
            return False

        # Validate price
        try:
            price = float(alert_data['price'])
            if price <= 0:
                logger.error(f'Invalid price: {alert_data["price"]}')
                return False
        except (ValueError, TypeError):
            logger.error(f'Invalid price: {alert_data["price"]}')
            return False

        # Validate size (at least one size field must be present)
        if not any(key in alert_data for key in ['size', 'sizeUsd', 'sizeByLeverage']):
            logger.error('No size specified (size, sizeUsd, or sizeByLeverage required)')
            return False

        # Validate sizeByLeverage if present
        if 'sizeByLeverage' in alert_data:
            try:
                leverage = float(alert_data['sizeByLeverage'])
                if leverage <= 0 or leverage > 1:
                    logger.error(f'Invalid sizeByLeverage: {alert_data["sizeByLeverage"]}')
                    return False
            except (ValueError, TypeError):
                logger.error(f'Invalid sizeByLeverage: {alert_data["sizeByLeverage"]}')
                return False

        logger.info('Alert validation passed')
        return True
        
    except Exception as e:
        logger.error(f'Error validating alert: {e}')
        return False

# Initialize trader
trader = HyperliquidTrader()

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "OK", "message": "TradingView Alert Connector is running"})

@app.route('/accounts', methods=['GET'])
def get_accounts():
    """Get account status endpoint"""
    logger.info('Received GET request for account status.')
    
    try:
        status = trader.get_account_status()
        return jsonify({"Hyperliquid": status})
    except Exception as error:
        logger.error(f'Failed to get account readiness: {error}')
        return jsonify({"error": "Internal server error"}), 500

@app.route('/', methods=['POST'])
def handle_alert():
    """Handle TradingView webhook alerts"""
    try:
        alert_data = request.get_json()
        logger.info(f'Received TradingView strategy alert: {alert_data}')

        # Validate alert
        if not validate_alert(alert_data):
            return jsonify({"error": "Alert message is not valid"}), 400

        # Check if client is ready
        status = trader.get_account_status()
        if not status.get('ready'):
            return jsonify({"error": "Hyperliquid account is not ready"}), 500

        # Place the order
        result = trader.place_order(alert_data)
        
        if result.get('success'):
            logger.info(f'Order placed successfully: {result}')
            return jsonify({"status": "OK", "order": result})
        else:
            logger.error(f'Order failed: {result.get("error")}')
            return jsonify({"error": result.get("error", "Unknown error")}), 500

    except Exception as error:
        logger.error(f'Error processing alert: {error}')
        return jsonify({"error": "Error processing order"}), 500

@app.route('/debug-sentry', methods=['GET'])
def debug_sentry():
    """Debug endpoint for Sentry"""
    raise Exception('My first Sentry error!')

if __name__ == '__main__':
    port = int(os.getenv('PORT', 3000))
    debug = os.getenv('NODE_ENV') != 'production'
    
    logger.info(f'Starting TradingView Alert Connector on port {port}')
    app.run(host='0.0.0.0', port=port, debug=debug) 