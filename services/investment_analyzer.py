"""Service for analyzing investment opportunities"""
from decimal import Decimal
from typing import Dict, List, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class InvestmentOption:
    product_id: str
    coin: str
    apy: Decimal
    duration: int  # in days
    min_amount: Decimal
    max_amount: Optional[Decimal]
    type: str  # 'STAKING', 'SAVINGS', 'LAUNCHPOOL'


class InvestmentAnalyzer:
    def __init__(self, binance_client):
        self.client = binance_client

    async def analyze_opportunities(self) -> Dict[str, str]:
        """Analyze current investment opportunities"""
        try:
            # Get staking products
            staking_products = await self.client.get_staking_products()
            # Get savings products
            savings_products = await self.client.get_savings_products()
            # Get launchpool products
            launchpool_products = await self.client.get_launchpool_products()

            # Combine all products
            all_products = []
            all_products.extend(self._parse_staking_products(staking_products))
            all_products.extend(self._parse_savings_products(savings_products))
            all_products.extend(self._parse_launchpool_products(launchpool_products))

            if not all_products:
                return {
                    "status": "info",
                    "message": "No investment opportunities found at the moment"
                }

            # Sort by APY
            sorted_products = sorted(
                all_products,
                key=lambda x: x.apy,
                reverse=True
            )

            # Format response message
            message = "📊 Best Investment Opportunities:\n\n"
            for i, product in enumerate(sorted_products[:5], 1):
                message += (
                    f"{i}. {product.coin} ({product.type})\n"
                    f"   APY: {product.apy}%\n"
                    f"   Duration: {product.duration} days\n"
                    f"   Min Amount: {product.min_amount} {product.coin}\n"
                    f"   {'Max Amount: ' + str(product.max_amount) + ' ' + product.coin if product.max_amount else 'No max amount'}\n\n"
                )

            return {
                "status": "success",
                "message": message,
                "best_option": sorted_products[0] if sorted_products else None
            }

        except Exception as e:
            logger.error(f"Error analyzing investment opportunities: {str(e)}")
            return {
                "status": "error",
                "message": "❌ Failed to analyze investment opportunities"
            }

    def _parse_staking_products(self, products: List[Dict]) -> List[InvestmentOption]:
        """Parse staking products into InvestmentOption objects"""
        result = []
        for product in products:
            try:
                result.append(InvestmentOption(
                    product_id=product['id'],
                    coin=product['asset'],
                    apy=Decimal(product['apy']),
                    duration=int(product['duration']),
                    min_amount=Decimal(product['minAmount']),
                    max_amount=Decimal(product['maxAmount']) if product.get('maxAmount') else None,
                    type='STAKING'
                ))
            except (KeyError, ValueError) as e:
                logger.warning(f"Error parsing staking product: {str(e)}")
        return result

    def _parse_savings_products(self, products: List[Dict]) -> List[InvestmentOption]:
        """Parse savings products into InvestmentOption objects"""
        result = []
        for product in products:
            try:
                result.append(InvestmentOption(
                    product_id=product['id'],
                    coin=product['asset'],
                    apy=Decimal(product['interestRate']),
                    duration=int(product['duration']),
                    min_amount=Decimal(product['minAmount']),
                    max_amount=Decimal(product['maxAmount']) if product.get('maxAmount') else None,
                    type='SAVINGS'
                ))
            except (KeyError, ValueError) as e:
                logger.warning(f"Error parsing savings product: {str(e)}")
        return result

    def _parse_launchpool_products(self, products: List[Dict]) -> List[InvestmentOption]:
        """Parse launchpool products into InvestmentOption objects"""
        result = []
        for product in products:
            try:
                result.append(InvestmentOption(
                    product_id=product['id'],
                    coin=product['asset'],
                    apy=Decimal(product['apy']),
                    duration=int(product['duration']),
                    min_amount=Decimal(product['minAmount']),
                    max_amount=Decimal(product['maxAmount']) if product.get('maxAmount') else None,
                    type='LAUNCHPOOL'
                ))
            except (KeyError, ValueError) as e:
                logger.warning(f"Error parsing launchpool product: {str(e)}")
        return result