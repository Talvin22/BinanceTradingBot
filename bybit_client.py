from pybit.unified_trading import HTTP
from config import BYBIT_API_KEY, BYBIT_API_SECRET
import logging

logger = logging.getLogger(__name__)


class BybitClient:
    def __init__(self):
        self.session = HTTP(
            api_key=BYBIT_API_KEY,
            api_secret=BYBIT_API_SECRET,
            testnet=False
        )

    async def get_wallet_balance(self):
        try:
            # Get wallet balance for SPOT account type
            response = self.session.get_wallet_balance(
                accountType="SPOT"
            )

            logger.info("Received response from Bybit API")

            if response and 'result' in response and 'list' in response['result']:
                # Extract the first wallet's details
                wallet = response['result']['list'][0]
                total_equity = float(wallet.get('totalEquity', 0))
                available_balance = float(wallet.get('availableBalance', 0))

                return (
                    "💰 Wallet Balance:\n"
                    f"Total Equity: {total_equity:.2f} USDT\n"
                    f"Available Balance: {available_balance:.2f} USDT"
                )
            else:
                logger.error(f"Unexpected API response structure: {response}")
                return "❌ Unable to parse balance information"

        except Exception as e:
            logger.error(f"Error fetching balance: {str(e)}")
            return f"❌ Error: {str(e)}"