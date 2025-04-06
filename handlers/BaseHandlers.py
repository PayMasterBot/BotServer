from aiogram import F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards import keyboards
from handlers import SubscriptionHandlers, CategoryHandlers, SpendingsHandlers, CurrencyHandlers, BinanceHandlers


class BaseStates(StatesGroup):
    IN_EXPENSES = State()
    IN_ASSETS = State()
    IN_MAIN = State()


def register_base_handlers(dp):
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(back_handler, F.text == "назад")
    dp.message.register(expenses_handler, F.text == "траты")
    dp.message.register(assets_handler, F.text == "активы")


async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer("Выберите раздел:", reply_markup=keyboards.get_main_kb())
    await state.set_state(BaseStates.IN_MAIN)


async def back_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    print(current_state)
    # await state.clear()

    if current_state == SubscriptionHandlers.SubscriptionStates.WAITING_SUBSCR_NAME.state or \
            current_state == SubscriptionHandlers.SubscriptionStates.WAITING_SUBSCR_PRICE.state or \
            current_state == SubscriptionHandlers.SubscriptionStates.WAITING_SUBSCR_DELETE_NUMBER.state:
        await state.set_state(SubscriptionHandlers.SubscriptionStates.IN_SUBSCRIPTIONS)
        await SubscriptionHandlers.show_subscriptions(message)

    elif current_state == CategoryHandlers.CategoryStates.WAITING_CATEGORY_NAME.state or \
            current_state == CategoryHandlers.CategoryStates.WAITING_CATEGORY_DELETE_NUMBER.state:
        await state.set_state(CategoryHandlers.CategoryStates.IN_CATEGORY)
        await CategoryHandlers.show_category(message)

    elif current_state == SpendingsHandlers.SpendingsStates.WAITING_SPENDING_CATEGORY.state or \
            current_state == SpendingsHandlers.SpendingsStates.WAITING_SPENDING_COST.state:
        await message.answer("Меню трат", reply_markup=keyboards.get_expenses_kb())
        await state.set_state(BaseStates.IN_EXPENSES)

    elif current_state == CurrencyHandlers.CurrencyStates.WAITING_PARE_NAME or \
            current_state == CurrencyHandlers.CurrencyStates.IN_TRACKED_PARES_LIST:
        await message.answer("Валюты", reply_markup=keyboards.get_currency_kb())
        await state.set_state(CurrencyHandlers.CurrencyStates.IN_CURRENCY)

    elif current_state == CurrencyHandlers.CurrencyStates.WAITING_NEW_TRACKED_PARE_NAME or \
            current_state == CurrencyHandlers.CurrencyStates.WAITING_TRACKED_PARE_DELETE_NUMBER:
        await CurrencyHandlers.tracked_pares_handler(message, state)

    elif current_state == BinanceHandlers.BinanceStates.WAITING_NEW_TRACKED_CRYPTO_PARE_NAME or \
            current_state == BinanceHandlers.BinanceStates.WAITING_TRACKED_CRYPTO_PARE_DELETE_NUMBER:
        await BinanceHandlers.tracked_crypto_pares_handler(message, state)

    elif current_state == BinanceHandlers.BinanceStates.WAITING_CRYPTO_PARE_NAME or \
            current_state == BinanceHandlers.BinanceStates.IN_TRACKED_CRYPTO_PARES_LIST:
        await message.answer("Крипто", reply_markup=keyboards.get_crypto_kb())
        await state.set_state(BinanceHandlers.BinanceStates.IN_BINANCE)

    elif message.text == "подписки":
        await SubscriptionHandlers.show_subscriptions(message)

    elif current_state == BaseStates.IN_EXPENSES or current_state == BaseStates.IN_ASSETS:
        await message.answer("Главное меню", reply_markup=keyboards.get_main_kb())
        await state.set_state(BaseStates.IN_MAIN)

    elif current_state == SubscriptionHandlers.SubscriptionStates.IN_SUBSCRIPTIONS or \
            current_state == CategoryHandlers.CategoryStates.IN_CATEGORY or \
            current_state == SpendingsHandlers.SpendingsStates.SPENDINGS_ANALYTICS:
        await message.answer("Меню трат", reply_markup=keyboards.get_expenses_kb())
        await state.set_state(BaseStates.IN_EXPENSES)

    elif current_state == CurrencyHandlers.CurrencyStates.IN_CURRENCY or \
            current_state == BinanceHandlers.BinanceStates.IN_BINANCE:
        await message.answer("Меню активов:", reply_markup=keyboards.get_assets_kb())
        await state.set_state(BaseStates.IN_ASSETS)


async def expenses_handler(message: types.Message, state: FSMContext):
    await message.answer("Меню трат:", reply_markup=keyboards.get_expenses_kb())
    await state.set_state(BaseStates.IN_EXPENSES)


async def assets_handler(message: types.Message, state: FSMContext):
    await message.answer("Меню активов:", reply_markup=keyboards.get_assets_kb())
    await state.set_state(BaseStates.IN_ASSETS)
