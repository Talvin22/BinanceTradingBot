from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from services.binance_client import BinanceClient
from config import BINANCE_API_KEY, BINANCE_API_SECRET
from decimal import Decimal, InvalidOperation
import logging

logger = logging.getLogger(__name__)

# Initialize router and client
router = Router()
binance_client = BinanceClient(BINANCE_API_KEY, BINANCE_API_SECRET)


class OrderStates(StatesGroup):
    waiting_for_symbol = State()
    waiting_for_quantity = State()
    waiting_for_confirmation = State()


TRADING_HELP_MESSAGE = """
📈 Testnet Trading Commands:

/test_buy - Test buying coins (using testnet)
/test_sell - Test selling coins (using testnet)
/cancel - Cancel current operation

Note: All operations use testnet - no real funds are involved.
"""


@router.message(Command("trading_help"))
async def cmd_trading_help(message: types.Message):
    """Show trading help message"""
    await message.answer(TRADING_HELP_MESSAGE)


@router.message(Command("test_buy"))
async def cmd_test_buy(message: types.Message, state: FSMContext):
    """Start test buy process"""
    await state.update_data(order_type="BUY")
    await state.set_state(OrderStates.waiting_for_symbol)
    await message.answer(
        "Enter the trading pair (e.g., BTCUSDT):"
    )


@router.message(Command("test_sell"))
async def cmd_test_sell(message: types.Message, state: FSMContext):
    """Start test sell process"""
    await state.update_data(order_type="SELL")
    await state.set_state(OrderStates.waiting_for_symbol)
    await message.answer(
        "Enter the trading pair (e.g., BTCUSDT):"
    )


@router.message(OrderStates.waiting_for_symbol)
async def process_symbol(message: types.Message, state: FSMContext):
    """Process trading pair input"""
    symbol = message.text.upper()

    # Get current market price
    price = await binance_client.get_market_price(symbol)
    if not price:
        await message.answer("❌ Invalid trading pair or error fetching price")
        await state.clear()
        return

    await state.update_data(symbol=symbol, price=price)
    await state.set_state(OrderStates.waiting_for_quantity)

    data = await state.get_data()
    order_type = data.get("order_type", "BUY")

    await message.answer(
        f"Current price of {symbol}: {price} USDT\n"
        f"Enter quantity to {order_type.lower()} (e.g., 0.001):"
    )


@router.message(OrderStates.waiting_for_quantity)
async def process_quantity(message: types.Message, state: FSMContext):
    """Process quantity input"""
    try:
        quantity = Decimal(message.text)
        if quantity <= 0:
            raise ValueError("Quantity must be positive")

        data = await state.get_data()
        symbol = data["symbol"]
        price = data["price"]
        order_type = data.get("order_type", "BUY")

        total_cost = quantity * price

        await state.update_data(quantity=quantity)
        await state.set_state(OrderStates.waiting_for_confirmation)

        await message.answer(
            f"📝 {order_type} Order Summary (TESTNET MODE):\n"
            f"Symbol: {symbol}\n"
            f"Quantity: {quantity}\n"
            f"Estimated Total: {total_cost:.2f} USDT\n\n"
            f"Send 'confirm' to place test order or 'cancel' to abort\n\n"
            "Note: This is a testnet order, no real funds will be used."
        )

    except (ValueError, InvalidOperation):
        await message.answer("❌ Please enter a valid number")


@router.message(OrderStates.waiting_for_confirmation, F.text.lower() == "confirm")
async def process_confirmation(message: types.Message, state: FSMContext):
    """Process order confirmation"""
    data = await state.get_data()

    result = await binance_client.place_test_order(
        symbol=data["symbol"],
        side=data.get("order_type", "BUY"),
        quantity=data["quantity"]
    )

    await message.answer(result["message"])
    await state.clear()


@router.message(OrderStates.waiting_for_confirmation, F.text.lower() == "cancel")
async def process_cancellation(message: types.Message, state: FSMContext):
    """Process order cancellation"""
    await message.answer("❌ Order cancelled")
    await state.clear()


@router.message(Command("cancel"))
async def cmd_cancel(message: types.Message, state: FSMContext):
    """Cancel current operation"""
    current_state = await state.get_state()
    if current_state is not None:
        await state.clear()
        await message.answer("❌ Operation cancelled")
    else:
        await message.answer("No active operation to cancel")