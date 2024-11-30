"""Service for automatic investment management"""
from decimal import Decimal
from typing import Dict, List, Optional
import logging
from .investment_analyzer import InvestmentAnalyzer, InvestmentOption

logger = logging.getLogger(__name__)


class AutoInvestor:
    def __init__(self, binance_client, investment_analyzer: InvestmentAnalyzer):
        self.client = binance_client
        self.analyzer = investment_analyzer
        self.auto_invest_enabled = False

    def toggle_auto_invest(self) -> bool:
        """Toggle auto-investment mode"""
        self.auto_invest_enabled = not self.auto_invest_enabled
        return self.auto_invest_enabled

    async def check_and_invest(self) -> Dict[str, str]:
        """Check for investment opportunities and invest if auto-invest is enabled"""
        if not self.auto_invest_enabled:
            return {
                "status": "info",
                "message": "Auto-invest is disabled. Use /auto_invest to enable."
            }

        try:
            # Analyze opportunities
            analysis = await self.analyzer.analyze_opportunities()
            if analysis["status"] != "success" or not analysis.get("best_option"):
                return analysis

            best_option = analysis["best_option"]

            # Get available balance
            balance = await self.client.get_wallet_balance()
            if balance["status"] != "success":
                return balance

            available_amount = Decimal(balance.get("available_amount", 0))
            if available_amount < best_option.min_amount:
                return {
                    "status": "info",
                    "message": (
                        f"Insufficient balance for auto-investment.\n"
                        f"Required: {best_option.min_amount} {best_option.coin}\n"
                        f"Available: {available_amount} {best_option.coin}"
                    )
                }

            # Calculate investment amount
            invest_amount = min(
                available_amount,
                best_option.max_amount or available_amount
            )

            # Place investment
            result = await self.client.stake_coins(
                product_id=best_option.product_id,
                amount=invest_amount
            )

            if result["status"] == "success":
                return {
                    "status": "success",
                    "message": (
                        "✅ Auto-investment successful!\n\n"
                        f"Product: {best_option.coin} {best_option.type}\n"
                        f"Amount: {invest_amount} {best_option.coin}\n"
                        f"APY: {best_option.apy}%\n"
                        f"Duration: {best_option.duration} days"
                    )
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error in auto-investment: {str(e)}")
            return {
                "status": "error",
                "message": "❌ Auto-investment failed"
            }

    async def get_active_investments(self) -> Dict[str, str]:
        """Get list of active investments"""
        try:
            investments = await self.client.get_staking_positions()

            if not investments:
                return {
                    "status": "info",
                    "message": "No active investments found"
                }

            message = "📈 Your Active Investments:\n\n"
            for inv in investments:
                message += (
                    f"🪙 {inv['asset']} ({inv['type']})\n"
                    f"Amount: {inv['amount']} {inv['asset']}\n"
                    f"APY: {inv['apy']}%\n"
                    f"Duration: {inv['duration']} days\n"
                    f"Status: {inv['status']}\n\n"
                )

            return {
                "status": "success",
                "message": message
            }

        except Exception as e:
            logger.error(f"Error fetching active investments: {str(e)}")
            return {
                "status": "error",
                "message": "❌ Failed to fetch active investments"
            }