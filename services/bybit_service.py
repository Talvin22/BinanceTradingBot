from typing import Dict
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)


class BybitService:
    def __init__(self, session):
        self.session = session

    async def get_wallet_balance(self) -> Dict[str, str]:
        """Get testnet wallet balance"""
        try:
            response = self.session.get_wallet_balance(
                accountType="UNIFIED"
            )

            if response and response.get("retCode") == 0 and response["result"]["list"]:
                wallet = response["result"]["list"][0]
                coins = wallet.get("coin", [])

                if not coins:
                    return {
                        "status": "success",
                        "message": (
                            "💰 Testnet Wallet Balance: 0.00 USDT\n\n"
                            "ℹ️ Your testnet wallet is empty. Use /get_funds to request test USDT."
                        )
                    }

                # Find USDT balance
                usdt_coin = next((coin for coin in coins if coin["coin"] == "USDT"), None)
                total_balance = Decimal(usdt_coin["walletBalance"]) if usdt_coin else Decimal("0")

                message = (
                    "💰 Testnet Wallet Balance:\n"
                    f"Available USDT: {total_balance:.2f}\n\n"
                )

                if total_balance == 0:
                    message += "ℹ️ Your testnet wallet is empty. Use /get_funds to request test USDT."

                return {
                    "status": "success",
                    "message": message
                }
            else:
                error_msg = response.get("retMsg", "Unknown error")
                logger.error(f"Failed to fetch wallet balance: {error_msg}")
                return {
                    "status": "error",
                    "message": "❌ Failed to fetch wallet balance"
                }

        except Exception as e:
            logger.error(f"Error fetching wallet balance: {str(e)}")
            return {
                "status": "error",
                "message": "❌ Error accessing wallet balance"
            }