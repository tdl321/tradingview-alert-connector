import { AlertObject, HyperliquidOrderParams, OrderResult } from '../types';
import { spawn } from 'child_process';
import { promisify } from 'util';
import config = require('config');
import 'dotenv/config';

export class HyperliquidClientService {
	private pythonPath: string;

	constructor() {
		this.pythonPath = process.env.PYTHON_PATH || 'python';
	}

	private async executePythonCommand(command: string, args: string[] = []): Promise<any> {
		return new Promise((resolve, reject) => {
			const pythonProcess = spawn(this.pythonPath, ['hyperliquid_trader.py', command, ...args]);
			
			let stdout = '';
			let stderr = '';

			pythonProcess.stdout.on('data', (data) => {
				stdout += data.toString();
			});

			pythonProcess.stderr.on('data', (data) => {
				stderr += data.toString();
			});

			pythonProcess.on('close', (code) => {
				if (code === 0) {
					try {
						const result = JSON.parse(stdout);
						resolve(result);
					} catch (error) {
						reject(new Error(`Failed to parse Python output: ${stdout}`));
					}
				} else {
					reject(new Error(`Python script failed with code ${code}: ${stderr}`));
				}
			});

			pythonProcess.on('error', (error) => {
				reject(new Error(`Failed to execute Python script: ${error.message}`));
			});
		});
	}

	getIsAccountReady = async (): Promise<boolean> => {
		try {
			const result = await this.executePythonCommand('status');
			console.log('Hyperliquid account status:', result);
			return result.ready === true;
		} catch (error) {
			console.error('Error checking account readiness:', error);
			return false;
		}
	};

	getAccountEquity = async (): Promise<number> => {
		try {
			const result = await this.executePythonCommand('equity');
			console.log('Hyperliquid Account Equity:', result.equity);
			return result.equity || 0;
		} catch (error) {
			console.error('Error getting account equity:', error);
			return 0;
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

	placeOrder = async (alertMessage: AlertObject): Promise<OrderResult> => {
		try {
			// Send the entire alert message to Python script
			const alertJson = JSON.stringify(alertMessage);
			const result = await this.executePythonCommand('order', [alertJson]);
			
			if (!result.success) {
				throw new Error(result.error || 'Unknown error from Python script');
			}

			const orderResult: OrderResult = {
				orderId: result.order_id,
				size: result.size,
				side: result.side
			};

			console.log('Order placed successfully:', orderResult);
			return orderResult;
		} catch (error) {
			console.error('Error placing order:', error);
			throw error;
		}
	};
} 