from decimal import Decimal
from typing import Dict, Optional, List
import logging

logger = logging.getLogger(__name__)


class TradingService:
    def __init__(self, session):
        self.session = session

    async def get_testnet_funds(self) -> Dict[str, str]:
        """Get testnet funds from Bybit"""
        try:
            # Create test USDT deposit
            response = self.session.create_internal_deposit(
                coin="USDT",
                amount="1000",
                accountType="UNIFIED"
            )

            if response and response.get("retCode") == 0:
                return {
                    "status": "success",
                    "message": (
                        "✅ Test funds (1000 USDT) have been requested!\n"
                        "Please check your balance in a few minutes using /balance command."
                    )
                }
            else:
                error_msg = response.get("retMsg", "Unknown error")
                logger.error(f"Failed to get testnet funds: {error_msg}")
                return {
                    "status": "error",
                    "message": f"❌ Failed to request testnet funds: {error_msg}"
                }

        except Exception as e:
            logger.error(f"Error requesting testnet funds: {str(e)}")
            return {
                "status": "error",
                "message": "❌ Error requesting testnet funds. Please try again later."
            }

    async def get_available_symbols(self) -> List[str]:
        """Get list of available trading pairs"""
        try:
            response = self.session.get_tickers(
                category="spot"
            )

            if response and response.get("retCode") == 0:
                return [
                    item["symbol"]
                    for item in response["result"]["list"]
                    if "symbol" in item
                ]
            return []

        except Exception as e:
            logger.error(f"Error fetching symbols: {str(e)}")
            return []

    async def place_test_order(
            self,
            symbol: str,
            side: str,
            quantity: Decimal,
            price: Optional[Decimal] = None
    ) -> Dict[str, str]:
        """Place a test order on Bybit testnet"""
        try:
            order_type = "MARKET" if price is None else "LIMIT"

            params = {
                "category": "spot",
                "symbol": symbol,
                "side": side,
                "orderType": order_type,
                "qty": str(quantity),
            }

            if price is not None:
                params["price"] = str(price)

            response = self.session.place_order(**params)

            if response and response.get("retCode") == 0:
                order_id = response.get("result", {}).get("orderId")
                return {
                    "status": "success",
                    "message": (
                        f"✅ Test order placed successfully!\n"
                        f"Order Type: {order_type}\n"
                        f"Symbol: {symbol}\n"
                        f"Quantity: {quantity}\n"
                        f"Order ID: {order_id}\n\n"
                        "Note: This is a testnet order, no real funds were used."
                    )
                }
            else:
                error_msg = response.get("retMsg", "Unknown error")
                logger.error(f"Order placement failed: {error_msg}")
                return {
                    "status": "error",
                    "message": f"❌ Order failed: {error_msg}"
                }

        except Exception as e:
            logger.error(f"Error placing test order: {str(e)}")
            return {
                "status": "error",
                "message": "❌ Failed to place test order. Please try again."
            }

    async def get_market_price(self, symbol: str) -> Optional[Decimal]:
        """Get current market price for a symbol"""
        try:
            response = self.session.get_tickers(
                category="spot",
                symbol=symbol
            )

            if response and response.get("retCode") == 0 and response["result"]["list"]:
                return Decimal(response["result"]["list"][0]["lastPrice"])
            return None

        except Exception as e:
            logger.error(f"Error fetching market price: {str(e)}")
            return None