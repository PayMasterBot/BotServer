from aiogram import F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards import keyboards
from handlers import BaseHandlers


class BinanceStates(StatesGroup):
    IN_BINANCE = State()
    WAITING_CRYPTO_PARE_NAME = State()
    WAITING_NEW_TRACKED_CRYPTO_PARE_NAME = State()
    WAITING_TRACKED_CRYPTO_PARE_DELETE_NUMBER = State()
    IN_TRACKED_CRYPTO_PARES_LIST = State()


def register_binance_handlers(dp):
    dp.message.register(binance_handler, F.text == "крипто")
    dp.message.register(get_crypto_pare_start, F.text == "запросить пару", BinanceStates.IN_BINANCE)
    dp.message.register(get_crypto_pare_name, BinanceStates.WAITING_CRYPTO_PARE_NAME)
    dp.message.register(get_analysis, F.text == "отчет", BinanceStates.IN_BINANCE)
    dp.message.register(tracked_crypto_pares_handler, F.text == "отслеживаемое", BinanceStates.IN_BINANCE)
    dp.message.register(add_new_tracked_crypto_pare_start, F.text == "добавить",
                        BinanceStates.IN_TRACKED_CRYPTO_PARES_LIST)
    dp.message.register(add_new_tracked_crypto_pare_name, BinanceStates.WAITING_NEW_TRACKED_CRYPTO_PARE_NAME)
    dp.message.register(delete_tracked_crypto_pare_start, F.text == "удалить",
                        BinanceStates.IN_TRACKED_CRYPTO_PARES_LIST)
    dp.message.register(delete_tracked_crypto_pare_number, BinanceStates.WAITING_TRACKED_CRYPTO_PARE_DELETE_NUMBER)
    dp.message.register(get_balance, F.text == "баланс")


async def binance_handler(message: types.Message, state: FSMContext):
    await message.answer("Валюты", reply_markup=keyboards.get_crypto_kb())
    await state.set_state(BinanceStates.IN_BINANCE)


async def get_crypto_pare_start(message: types.Message, state: FSMContext):
    await message.answer("Введите название пары", reply_markup=keyboards.get_back_kb())
    await state.set_state(BinanceStates.WAITING_CRYPTO_PARE_NAME)


async def get_crypto_pare_name(message: types.Message, state: FSMContext):
    if message.text == "назад":
        await state.clear()
        return

    # получить информацию о паре

    await message.answer(
        "0.32462",
        reply_markup=keyboards.get_crypto_kb()
    )
    await state.set_state(BinanceStates.IN_BINANCE)


async def get_analysis(message: types.Message, state: FSMContext):
    # формирование отчета
    await message.answer("Ваш отчет: ", reply_markup=keyboards.get_crypto_kb())
    await state.set_state(BinanceStates.IN_BINANCE)


async def tracked_crypto_pares_handler(message: types.Message, state: FSMContext):
    await show_tracked_crypto_pares(message)
    await state.set_state(BinanceStates.IN_TRACKED_CRYPTO_PARES_LIST)


async def show_tracked_crypto_pares(message: types.Message):
    # получение списка отслеживаемых пар
    await message.answer("Ваш список отслеживаемых пар: ", reply_markup=keyboards.get_tracked_pares_kb())


async def add_new_tracked_crypto_pare_start(message: types.Message, state: FSMContext):
    await message.answer("Введите название новой пары: ", reply_markup=keyboards.get_back_kb())
    await state.set_state(BinanceStates.WAITING_NEW_TRACKED_CRYPTO_PARE_NAME)


async def add_new_tracked_crypto_pare_name(message: types.Message, state: FSMContext):
    if message.text == "назад":
        await state.clear()
        return

    # получить имя новой пары

    await message.answer("Новая пара добавлена", reply_markup=keyboards.get_tracked_pares_kb())
    await state.set_state(BinanceStates.IN_TRACKED_CRYPTO_PARES_LIST)


async def delete_tracked_crypto_pare_start(message: types.Message, state: FSMContext):
    await show_tracked_crypto_pares(message)
    await message.answer("Введите номер удаляемой пары: ", reply_markup=keyboards.get_back_kb())
    await state.set_state(BinanceStates.WAITING_TRACKED_CRYPTO_PARE_DELETE_NUMBER)


async def delete_tracked_crypto_pare_number(message: types.Message, state: FSMContext):
    if message.text == "назад":
        await state.clear()
        return

    # получение номера пары и удаление

    await message.answer("Пара удалена", reply_markup=keyboards.get_tracked_pares_kb())
    await state.set_state(BinanceStates.IN_TRACKED_CRYPTO_PARES_LIST)


async def get_balance(message: types.Message, state: FSMContext):
    # получение баланса
    await message.answer("Ваш баланс: 100$", reply_markup=keyboards.get_crypto_kb())
    await state.set_state(BinanceStates.IN_BINANCE)
