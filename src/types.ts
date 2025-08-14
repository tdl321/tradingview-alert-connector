export type AlertObject = {
	exchange: string;
	strategy: string;
	market: string;
	size?: number;
	sizeUsd?: number;
	sizeByLeverage?: number;
	order: string;
	price: number;
	position: string;
	reverse: boolean;
	passphrase?: string;
};

export type HyperliquidOrderParams = {
	market: string;
	side: 'buy' | 'sell';
	size: number;
	price: number;
	leverage?: number;
};

export interface OrderResult {
	size: number;
	side: string;
	orderId: string;
}
