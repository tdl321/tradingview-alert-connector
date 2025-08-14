import { AlertObject } from '../types';

export const validateAlert = async (alertMessage: any): Promise<boolean> => {
	try {
		// Basic validation
		if (!alertMessage) {
			console.error('Alert message is empty');
			return false;
		}

		// Check required fields
		const requiredFields = ['exchange', 'strategy', 'market', 'order', 'price'];
		for (const field of requiredFields) {
			if (!alertMessage[field]) {
				console.error(`Missing required field: ${field}`);
				return false;
			}
		}

		// Validate exchange
		if (alertMessage.exchange.toLowerCase() !== 'hyperliquid') {
			console.error(`Unsupported exchange: ${alertMessage.exchange}`);
			return false;
		}

		// Validate order type
		if (!['buy', 'sell'].includes(alertMessage.order.toLowerCase())) {
			console.error(`Invalid order type: ${alertMessage.order}`);
			return false;
		}

		// Validate price
		if (typeof alertMessage.price !== 'number' || alertMessage.price <= 0) {
			console.error(`Invalid price: ${alertMessage.price}`);
			return false;
		}

		// Validate size (at least one size field must be present)
		if (!alertMessage.size && !alertMessage.sizeUsd && !alertMessage.sizeByLeverage) {
			console.error('No size specified (size, sizeUsd, or sizeByLeverage required)');
			return false;
		}

		// Validate sizeByLeverage if present
		if (alertMessage.sizeByLeverage) {
			const leverage = Number(alertMessage.sizeByLeverage);
			if (isNaN(leverage) || leverage <= 0 || leverage > 1) {
				console.error(`Invalid sizeByLeverage: ${alertMessage.sizeByLeverage}`);
				return false;
			}
		}

		console.log('Alert validation passed');
		return true;
	} catch (error) {
		console.error('Error validating alert:', error);
		return false;
	}
}; 