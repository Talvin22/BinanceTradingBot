from aiogram import Router, types
from aiogram.filters import Command
from services.binance_client import BinanceClient
from config import BINANCE_API_KEY, BINANCE_API_SECRET
import logging
from typing import Final

logger = logging.getLogger(__name__)

# Initialize router and client
router = Router()
binance_client = BinanceClient(BINANCE_API_KEY, BINANCE_API_SECRET)

# Command messages
WELCOME_MESSAGE: Final[str] = """
👋 Welcome {name} to Binance Trading Bot!

Available commands:
/balance - Check your testnet balance
/trading_help - Show trading commands
/help - Show all available commands
"""

HELP_MESSAGE: Final[str] = """
📚 Available Commands:

Basic Commands:
/balance - Check your testnet balance
/get_funds - Get testnet funds
/trading_help - Show trading commands
/start - Show welcome message
/help - Show this help message

For trading commands, use /trading_help
"""


@router.message(Command("start"))
async def cmd_start(message: types.Message) -> None:
    """Handle /start command"""
    user_name = message.from_user.first_name
    await message.answer(WELCOME_MESSAGE.format(name=user_name))


@router.message(Command("help"))
async def cmd_help(message: types.Message) -> None:
    """Handle /help command"""
    await message.answer(HELP_MESSAGE)


@router.message(Command("balance"))
async def cmd_balance(message: types.Message) -> None:
    """Handle /balance command"""
    try:
        user_id = message.from_user.id
        logger.info(f"Fetching balance for user {user_id}")

        status_message = await message.answer("🔄 Fetching wallet balance...")
        result = await binance_client.get_wallet_balance()

        # Send main balance message
        await status_message.edit_text(result["message"])

        # Send additional balance messages if any
        if result.get("additional_messages"):
            for additional_msg in result["additional_messages"]:
                await message.answer(additional_msg)

    except Exception as e:
        logger.error(f"Error in balance command: {str(e)}")
        await message.answer("❌ An error occurred. Please try again later.")


@router.message(Command("get_funds"))
async def cmd_get_funds(message: types.Message) -> None:
    """Handle /get_funds command"""
    try:
        status_message = await message.answer("🔄 Requesting test funds...")
        result = await binance_client.get_test_funds()

        await status_message.edit_text(result["message"])

    except Exception as e:
        logger.error(f"Error in get_funds command: {str(e)}")
        await message.answer("❌ Failed to request test funds. Please try again later.")