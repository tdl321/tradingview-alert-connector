import { AlertObject, HyperliquidOrderParams, OrderResult } from '../types';
import { HyperliquidClient } from 'hyperliquid-js-sdk';
import config = require('config');
import 'dotenv/config';

export class HyperliquidClientService {
	private client: HyperliquidClient;
	private wallet: any;

	constructor() {
		this.initializeClient();
	}

	private initializeClient() {
		try {
			if (!process.env.HYPERLIQUID_PRIVATE_KEY) {
				console.error('HYPERLIQUID_PRIVATE_KEY is not set');
				return;
			}

			// Initialize Hyperliquid client
			// Note: This is a placeholder - you'll need to check the actual Hyperliquid SDK documentation
			// for the correct initialization method
			this.client = new HyperliquidClient({
				network: 'mainnet', // or 'testnet'
				privateKey: process.env.HYPERLIQUID_PRIVATE_KEY
			});

			console.log('Hyperliquid client initialized');
		} catch (error) {
			console.error('Failed to initialize Hyperliquid client:', error);
		}
	}

	getIsAccountReady = async (): Promise<boolean> => {
		try {
			if (!this.client) {
				return false;
			}

			// Check account balance/status
			// This is a placeholder - implement based on Hyperliquid SDK
			const balance = await this.client.getBalance();
			console.log('Hyperliquid account balance:', balance);
			
			return balance > 0;
		} catch (error) {
			console.error('Error checking account readiness:', error);
			return false;
		}
	};

	buildOrderParams = async (alertMessage: AlertObject): Promise<HyperliquidOrderParams> => {
		const side = alertMessage.order === 'buy' ? 'buy' : 'sell';
		
		let size: number;

		// Support percentage-based order sizing using sizeByLeverage
		if (alertMessage.sizeByLeverage) {
			const equity = await this.getAccountEquity();
			size = equity * Number(alertMessage.sizeByLeverage);
		} else if (alertMessage.sizeUsd) {
			size = alertMessage.sizeUsd;
		} else if (alertMessage.size) {
			size = alertMessage.size;
		} else {
			throw new Error('Order size is not specified in alert message');
		}

		const orderParams: HyperliquidOrderParams = {
			market: alertMessage.market,
			side,
			size,
			price: alertMessage.price,
			leverage: Number(process.env.HYPERLIQUID_LEVERAGE) || 1
		};

		console.log('Order params for Hyperliquid:', orderParams);
		return orderParams;
	};

	getAccountEquity = async (): Promise<number> => {
		try {
			if (!this.client) {
				console.error('Client not initialized');
				return 0;
			}

			// Get account equity from Hyperliquid
			// This is a placeholder - implement based on Hyperliquid SDK
			const equity = await this.client.getEquity();
			console.log('Hyperliquid Account Equity:', equity);
			
			return equity;
		} catch (error) {
			console.error('Error getting account equity:', error);
			return 0;
		}
	};

	placeOrder = async (alertMessage: AlertObject): Promise<OrderResult> => {
		try {
			const orderParams = await this.buildOrderParams(alertMessage);
			const result = await this.createOrder(orderParams);
			
			console.log('Order placed successfully:', result);
			return result;
		} catch (error) {
			console.error('Error placing order:', error);
			throw error;
		}
	};

	createOrder = async (orderParams: HyperliquidOrderParams): Promise<OrderResult> => {
		try {
			if (!this.client) {
				throw new Error('Hyperliquid client not initialized');
			}

			// Place order using Hyperliquid SDK
			// This is a placeholder - implement based on Hyperliquid SDK
			const order = await this.client.placeOrder({
				market: orderParams.market,
				side: orderParams.side,
				size: orderParams.size,
				price: orderParams.price,
				leverage: orderParams.leverage
			});

			const orderResult: OrderResult = {
				orderId: order.id || 'unknown',
				size: orderParams.size,
				side: orderParams.side.toUpperCase()
			};

			return orderResult;
		} catch (error) {
			console.error('Error creating order:', error);
			throw error;
		}
	};
} 