"""Handlers for investment-related commands"""
from aiogram import Router, types
from aiogram.filters import Command
from services.investment_analyzer import InvestmentAnalyzer
from services.auto_investor import AutoInvestor
from services.binance_client import BinanceClient
from config import BINANCE_API_KEY, BINANCE_API_SECRET
import logging

logger = logging.getLogger(__name__)

# Initialize router and services
router = Router()
binance_client = BinanceClient(BINANCE_API_KEY, BINANCE_API_SECRET)
investment_analyzer = InvestmentAnalyzer(binance_client)
auto_investor = AutoInvestor(binance_client, investment_analyzer)

INVESTMENT_HELP_MESSAGE = """
💰 Investment Commands:

/analyze - Analyze best investment opportunities
/auto_invest - Toggle automatic investment mode
/investments - Show your active investments
/investment_help - Show this help message

Note: All operations use testnet - no real funds are involved.
"""


@router.message(Command("investment_help"))
async def cmd_investment_help(message: types.Message):
    """Show investment help message"""
    await message.answer(INVESTMENT_HELP_MESSAGE)


@router.message(Command("analyze"))
async def cmd_analyze(message: types.Message):
    """Analyze investment opportunities"""
    try:
        status_message = await message.answer("🔄 Analyzing investment opportunities...")
        result = await investment_analyzer.analyze_opportunities()

        await status_message.edit_text(result["message"])

    except Exception as e:
        logger.error(f"Error in analyze command: {str(e)}")
        await message.answer("❌ Failed to analyze investment opportunities")


@router.message(Command("auto_invest"))
async def cmd_auto_invest(message: types.Message):
    """Toggle auto-investment mode"""
    try:
        is_enabled = auto_investor.toggle_auto_invest()

        if is_enabled:
            status_message = await message.answer(
                "✅ Auto-investment mode enabled\n"
                "🔄 Checking investment opportunities..."
            )

            result = await auto_investor.check_and_invest()
            await status_message.edit_text(result["message"])
        else:
            await message.answer("❌ Auto-investment mode disabled")

    except Exception as e:
        logger.error(f"Error in auto_invest command: {str(e)}")
        await message.answer("❌ Failed to toggle auto-investment mode")


@router.message(Command("investments"))
async def cmd_investments(message: types.Message):
    """Show active investments"""
    try:
        status_message = await message.answer("🔄 Fetching your investments...")
        result = await auto_investor.get_active_investments()

        await status_message.edit_text(result["message"])

    except Exception as e:
        logger.error(f"Error in investments command: {str(e)}")
        await message.answer("❌ Failed to fetch investments")