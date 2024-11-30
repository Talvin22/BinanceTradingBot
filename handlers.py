from aiogram import Router, types
from aiogram.filters import Command
from services.bybit_service import BybitService
import logging
from typing import Final

logger = logging.getLogger(__name__)

# Initialize router and service
router: Final = Router()
bybit_service: Final = BybitService()

# Command messages
WELCOME_MESSAGE: Final[str] = """
👋 Welcome {name} to Bybit Balance Bot!

Available commands:
/balance - Check your current Bybit balance
/help - Show available commands
"""

HELP_MESSAGE: Final[str] = """
📚 Available Commands:

/balance - Check your current Bybit balance
/start - Show welcome message
/help - Show this help message
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

        status_message = await message.answer("🔄 Checking time synchronization...")
        balance = await bybit_service.get_wallet_balance()

        await status_message.edit_text(balance)

    except Exception as e:
        logger.error(f"Error in balance command: {str(e)}")
        await message.answer("❌ An error occurred. Please try again later.")