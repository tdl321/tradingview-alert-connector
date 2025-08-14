#!/usr/bin/env python3
"""
Hyperliquid Trading Service
Handles TradingView alerts and executes trades on Hyperliquid
"""

import json
import sys
import os
from typing import Dict, Any, Optional
from hyperliquid import HyperliquidSync
from eth_account import Account
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

def main():
    """Main function to handle command line arguments"""
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No command specified"}))
        return
    
    command = sys.argv[1]
    trader = HyperliquidTrader()
    
    if command == "status":
        # Get account status
        result = trader.get_account_status()
        print(json.dumps(result))
    
    elif command == "equity":
        # Get account equity
        equity = trader.get_account_equity()
        print(json.dumps({"equity": equity}))
    
    elif command == "order":
        # Place an order
        if len(sys.argv) < 3:
            print(json.dumps({"error": "No alert data provided"}))
            return
        
        try:
            alert_data = json.loads(sys.argv[2])
            result = trader.place_order(alert_data)
            print(json.dumps(result))
        except json.JSONDecodeError:
            print(json.dumps({"error": "Invalid JSON in alert data"}))
    
    else:
        print(json.dumps({"error": f"Unknown command: {command}"}))

if __name__ == "__main__":
    main() 