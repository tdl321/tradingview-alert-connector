import express, { Router } from 'express';
import { validateAlert } from '../services/validateAlert';
import { HyperliquidClientService } from '../services/hyperliquidClient';

const router: Router = express.Router();

// Health check endpoint
router.get('/', async (req, res) => {
	res.send('OK');
});

// Account status endpoint
router.get('/accounts', async (req, res) => {
	console.log('Received GET request for account status.');

	try {
		const hyperliquidClient = new HyperliquidClientService();
		const isReady = await hyperliquidClient.getIsAccountReady();

		const message = {
			Hyperliquid: isReady
		};
		
		res.send(message);
	} catch (error) {
		console.error('Failed to get account readiness:', error);
		res.status(500).send('Internal server error');
	}
});

// TradingView webhook endpoint
router.post('/', async (req, res) => {
	console.log('Received TradingView strategy alert:', req.body);

	try {
		const validated = await validateAlert(req.body);
		if (!validated) {
			res.status(400).send('Error: Alert message is not valid');
			return;
		}

		const hyperliquidClient = new HyperliquidClientService();
		
		// Check if client is ready
		const isReady = await hyperliquidClient.getIsAccountReady();
		if (!isReady) {
			res.status(500).send('Error: Hyperliquid account is not ready');
			return;
		}

		// Place the order
		const result = await hyperliquidClient.placeOrder(req.body);
		console.log('Order placed successfully:', result);

		res.send('OK');
	} catch (error) {
		console.error('Error processing alert:', error);
		res.status(500).send('Error processing order');
	}
});

// Debug endpoint for Sentry
router.get('/debug-sentry', function mainHandler(req, res) {
	throw new Error('My first Sentry error!');
});

export default router;
