#!/usr/bin/env python3
"""
Production startup script for TradingView Alert Connector
"""

import os
from app import app

if __name__ == '__main__':
    port = int(os.getenv('PORT', 3000))
    app.run(host='0.0.0.0', port=port, debug=False) 