from binance.client import Client
from binance.exceptions import BinanceAPIException
from decimal import Decimal
import logging
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)


class BinanceClient:
    def __init__(self, api_key: str, api_secret: str):
        self.client = Client(
            api_key=api_key,
            api_secret=api_secret,
            testnet=True  # Using testnet for testing
        )

    def _format_balance(self, balance: Dict[str, str]) -> str:
        """Format a single balance entry"""
        free = float(balance['free'])
        locked = float(balance['locked'])

        if free == 0 and locked == 0:
            return ""

        return (
            f"🪙 {balance['asset']}:\n"
            f"   Available: {free:.4f}\n"
            f"   Locked: {locked:.4f}\n"
        )

    def _chunk_balances(self, balances: List[Dict[str, str]], chunk_size: int = 10) -> List[str]:
        """Split balances into chunks to avoid message length limits"""
        messages = []
        current_chunk = []
        current_length = 0

        for balance in balances:
            formatted = self._format_balance(balance)
            if not formatted:
                continue

            if current_length >= chunk_size:
                messages.append("💰 Testnet Wallet Balance:\n\n" + "\n".join(current_chunk))
                current_chunk = []
                current_length = 0

            current_chunk.append(formatted)
            current_length += 1

        if current_chunk:
            messages.append("💰 Testnet Wallet Balance:\n\n" + "\n".join(current_chunk))

        return messages

    async def get_wallet_balance(self) -> Dict[str, str]:
        """Get testnet wallet balance"""
        try:
            account = self.client.get_account()
            balances = account['balances']

            # Filter and sort balances
            non_zero = [
                b for b in balances
                if float(b['free']) > 0 or float(b['locked']) > 0
            ]

            if not non_zero:
                return {
                    "status": "success",
                    "message": (
                        "💰 Testnet Wallet is empty\n\n"
                        "Use /get_funds to request test funds"
                    )
                }

            # Split balances into chunks
            messages = self._chunk_balances(non_zero)

            # Return first chunk with info about additional messages
            if len(messages) > 1:
                messages[0] += f"\n\n(Showing {len(messages)} parts. Additional balances in next messages)"

            return {
                "status": "success",
                "message": messages[0],
                "additional_messages": messages[1:] if len(messages) > 1 else []
            }

        except BinanceAPIException as e:
            logger.error(f"Binance API error: {str(e)}")
            return {
                "status": "error",
                "message": f"❌ API Error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Error fetching balance: {str(e)}")
            return {
                "status": "error",
                "message": "❌ Failed to fetch wallet balance"
            }

    async def get_market_price(self, symbol: str) -> Optional[Decimal]:
        """Get current market price for a symbol"""
        try:
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            return Decimal(ticker['price'])
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {str(e)}")
            return None

    async def place_test_order(
            self,
            symbol: str,
            side: str,
            quantity: Decimal
    ) -> Dict[str, str]:
        """Place a test order on Binance testnet"""
        try:
            order = self.client.create_test_order(
                symbol=symbol,
                side=side,
                type='MARKET',
                quantity=float(quantity)
            )

            return {
                "status": "success",
                "message": (
                    "✅ Test order simulation successful!\n\n"
                    f"Symbol: {symbol}\n"
                    f"Side: {side}\n"
                    f"Quantity: {quantity}\n"
                    f"Type: MARKET\n\n"
                    "Note: This was a test order, no actual trade was executed."
                )
            }

        except BinanceAPIException as e:
            logger.error(f"Binance API error: {str(e)}")
            return {
                "status": "error",
                "message": f"❌ Order Error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Error placing test order: {str(e)}")
            return {
                "status": "error",
                "message": "❌ Failed to place test order"
            }

    async def get_test_funds(self) -> Dict[str, str]:
        """Get test funds from Binance testnet"""
        try:
            # Create test orders to receive test funds
            self.client.create_test_order(
                symbol='BTCUSDT',
                side='BUY',
                type='MARKET',
                quantity=0.001
            )

            return {
                "status": "success",
                "message": (
                    "✅ Test funds request successful!\n\n"
                    "Check your balance in a few minutes using /balance\n"
                    "Note: This is on testnet, no real funds are involved."
                )
            }

        except BinanceAPIException as e:
            logger.error(f"Binance API error: {str(e)}")
            return {
                "status": "error",
                "message": f"❌ Error requesting test funds: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Error getting test funds: {str(e)}")
            return {
                "status": "error",
                "message": "❌ Failed to request test funds"
            }

