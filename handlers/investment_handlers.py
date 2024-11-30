from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from services.service_factory import ServiceFactory
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

# Initialize services
service_factory = ServiceFactory()
investment_service = service_factory.investment_service


class InvestmentStates(StatesGroup):
    choosing_coin = State()
    entering_amount = State()
    confirming_investment = State()
    choosing_exchange_from = State()
    choosing_exchange_to = State()
    entering_exchange_amount = State()


def register_investment_handlers(router: Router) -> None:
    """Register investment-related command handlers"""

    @router.message(Command("invest"))
    async def cmd_invest(message: types.Message, state: FSMContext):
        """Start investment process"""
        coins = await investment_service.get_available_coins()

        if not coins:
            await message.answer("❌ No coins available for investment at the moment")
            return

        keyboard = types.ReplyKeyboardMarkup(
            keyboard=[[types.KeyboardButton(text=coin)] for coin in coins],
            resize_keyboard=True
        )

        await state.set_state(InvestmentStates.choosing_coin)
        await message.answer(
            "Choose a coin to invest:",
            reply_markup=keyboard
        )

    @router.message(Command("investments"))
    async def cmd_investments(message: types.Message):
        """Show active investments"""
        positions = await investment_service.get_active_investments()

        if not positions:
            await message.answer("No active investments found")
            return

        response = "Your Active Investments:\n\n"
        for pos in positions:
            response += (
                f"🪙 {pos.coin}\n"
                f"Amount: {pos.amount}\n"
                f"APY: {pos.apy}%\n"
                f"Type: {pos.product_type.value}\n\n"
            )

        await message.answer(response)

    @router.message(Command("exchange"))
    async def cmd_exchange(message: types.Message, state: FSMContext):
        """Start coin exchange process"""
        coins = await investment_service.get_available_coins()

        if not coins:
            await message.answer("❌ No coins available for exchange")
            return

        keyboard = types.ReplyKeyboardMarkup(
            keyboard=[[types.KeyboardButton(text=coin)] for coin in coins],
            resize_keyboard=True
        )

        await state.set_state(InvestmentStates.choosing_exchange_from)
        await message.answer(
            "Choose coin to exchange from:",
            reply_markup=keyboard
        )

    @router.message(Command("auto_invest"))
    async def cmd_auto_invest(message: types.Message):
        """Toggle auto-investment mode"""
        await message.answer("Auto-investment mode is not implemented yet")