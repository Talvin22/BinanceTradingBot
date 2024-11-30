import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import TELEGRAM_BOT_TOKEN
from handlers import router
from utils.logging_config import setup_logging


async def main() -> None:
    """Main function to run the bot"""
    try:
        # Set up logging
        setup_logging()
        logger = logging.getLogger(__name__)
        logger.info("Starting bot...")

        # Initialize bot and dispatcher with FSM storage
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        dp = Dispatcher(storage=MemoryStorage())

        # Register handlers
        dp.include_router(router)

        # Delete webhook before polling
        await bot.delete_webhook(drop_pending_updates=True)

        # Start polling
        logger.info("Bot is running...")
        await dp.start_polling(bot)

    except Exception as e:
        logger.error(f"Error starting bot: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())