from typing import List, Dict, Optional
import logging
from decimal import Decimal
from pybit.unified_trading import HTTP
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class InvestmentType(Enum):
    STAKING = "STAKING"
    LAUNCHPOOL = "LAUNCHPOOL"
    LIQUIDITY_MINING = "LIQUIDITY_MINING"
    DUAL_INVESTMENT = "DUAL_INVESTMENT"


@dataclass
class InvestmentProduct:
    coin: str
    type: InvestmentType
    apy: Decimal
    duration: int  # in days
    min_amount: Decimal
    max_amount: Optional[Decimal]


@dataclass
class InvestmentPosition:
    coin: str
    amount: Decimal
    product_type: InvestmentType
    apy: Decimal
    start_time: int
    end_time: int


class InvestmentService:
    def __init__(self, session: HTTP):
        self.session = session

    async def get_available_coins(self) -> List[str]:
        """Get list of available coins for investment"""
        try:
            response = self.session.get_coins_info()
            if not response or 'result' not in response:
                return []

            return [
                coin['coin']
                for coin in response['result']['list']
                if coin.get('status') == 'LISTED'
            ]
        except Exception as e:
            logger.error(f"Error fetching available coins: {e}")
            return []

    async def get_investment_products(self, coin: str) -> List[InvestmentProduct]:
        """Get available investment products for a specific coin"""
        products = []

        try:
            # Get staking products
            staking = self.session.get_staking_products(coin=coin)
            if staking and 'result' in staking:
                for product in staking['result']['list']:
                    products.append(InvestmentProduct(
                        coin=coin,
                        type=InvestmentType.STAKING,
                        apy=Decimal(product['apy']),
                        duration=int(product['duration']),
                        min_amount=Decimal(product['minAmount']),
                        max_amount=Decimal(product['maxAmount']) if product.get('maxAmount') else None
                    ))

            # Add other product types here as they become available in the API

        except Exception as e:
            logger.error(f"Error fetching investment products for {coin}: {e}")

        return products

    async def find_best_investment(self, coin: str, amount: Decimal) -> Optional[InvestmentProduct]:
        """Find the best investment product for a given coin and amount"""
        products = await self.get_investment_products(coin)

        if not products:
            return None

        eligible_products = [
            p for p in products
            if p.min_amount <= amount and (not p.max_amount or amount <= p.max_amount)
        ]

        if not eligible_products:
            return None

        return max(eligible_products, key=lambda p: p.apy)

    async def auto_invest(self, coin: str, amount: Decimal) -> Dict[str, str]:
        """Automatically invest in the best available product"""
        try:
            best_product = await self.find_best_investment(coin, amount)
            if not best_product:
                return {
                    "status": "error",
                    "message": f"No suitable investment products found for {coin}"
                }

            # Execute investment based on product type
            if best_product.type == InvestmentType.STAKING:
                response = self.session.set_staking_position(
                    coin=coin,
                    amount=str(amount),
                    product_id=best_product.product_id
                )

                if response and response.get('ret_code') == 0:
                    return {
                        "status": "success",
                        "message": (
                            f"Successfully staked {amount} {coin}\n"
                            f"APY: {best_product.apy}%\n"
                            f"Duration: {best_product.duration} days"
                        )
                    }

            return {
                "status": "error",
                "message": "Failed to execute investment"
            }

        except Exception as e:
            logger.error(f"Error in auto-invest for {coin}: {e}")
            return {
                "status": "error",
                "message": f"Investment failed: {str(e)}"
            }

    async def get_active_investments(self) -> List[InvestmentPosition]:
        """Get list of active investment positions"""
        try:
            positions = []

            # Get staking positions
            response = self.session.get_staking_positions()
            if response and 'result' in response:
                for pos in response['result']['list']:
                    positions.append(InvestmentPosition(
                        coin=pos['coin'],
                        amount=Decimal(pos['amount']),
                        product_type=InvestmentType.STAKING,
                        apy=Decimal(pos['apy']),
                        start_time=int(pos['startTime']),
                        end_time=int(pos['endTime'])
                    ))

            return positions

        except Exception as e:
            logger.error(f"Error fetching active investments: {e}")
            return []

    async def exchange_coins(self, from_coin: str, to_coin: str, amount: Decimal) -> Dict[str, str]:
        """Exchange coins at market price"""
        try:
            symbol = f"{from_coin}{to_coin}"

            # Check if trading pair exists
            response = self.session.get_tickers(symbol=symbol)
            if not response or 'result' not in response:
                return {
                    "status": "error",
                    "message": f"Trading pair {symbol} not available"
                }

            # Execute market order
            order = self.session.place_order(
                symbol=symbol,
                side="SELL",
                orderType="MARKET",
                qty=str(amount)
            )

            if order and order.get('ret_code') == 0:
                return {
                    "status": "success",
                    "message": f"Successfully exchanged {amount} {from_coin} to {to_coin}"
                }

            return {
                "status": "error",
                "message": "Exchange failed"
            }

        except Exception as e:
            logger.error(f"Error exchanging coins: {e}")
            return {
                "status": "error",
                "message": f"Exchange failed: {str(e)}"
            }