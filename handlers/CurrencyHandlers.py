from aiogram import F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards import keyboards
from handlers import BaseHandlers


class CurrencyStates(StatesGroup):
    IN_CURRENCY = State()
    WAITING_PARE_NAME = State()
    WAITING_NEW_TRACKED_PARE_NAME = State()
    WAITING_TRACKED_PARE_DELETE_NUMBER = State()
    IN_TRACKED_PARES_LIST = State()


def register_currency_handlers(dp):
    dp.message.register(currency_handler, F.text == "валюты")
    dp.message.register(get_pare_start, F.text == "запросить пару", CurrencyStates.IN_CURRENCY)
    dp.message.register(get_pare_name, CurrencyStates.WAITING_PARE_NAME)
    dp.message.register(get_analysis, F.text == "отчет", CurrencyStates.IN_CURRENCY)
    dp.message.register(tracked_pares_handler, F.text == "отслеживаемое", CurrencyStates.IN_CURRENCY)
    dp.message.register(add_new_tracked_pare_start, F.text == "добавить", CurrencyStates.IN_TRACKED_PARES_LIST)
    dp.message.register(add_new_tracked_pare_name, CurrencyStates.WAITING_NEW_TRACKED_PARE_NAME)
    dp.message.register(delete_tracked_pare_start, F.text == "удалить", CurrencyStates.IN_TRACKED_PARES_LIST)
    dp.message.register(delete_tracked_pare_number, CurrencyStates.WAITING_TRACKED_PARE_DELETE_NUMBER)


async def currency_handler(message: types.Message, state: FSMContext):
    await message.answer("Валюты", reply_markup=keyboards.get_currency_kb())
    await state.set_state(CurrencyStates.IN_CURRENCY)


async def get_pare_start(message: types.Message, state: FSMContext):
    await message.answer("Введите название пары", reply_markup=keyboards.get_back_kb())
    await state.set_state(CurrencyStates.WAITING_PARE_NAME)


async def get_pare_name(message: types.Message, state: FSMContext):
    if message.text == "назад":
        await state.clear()
        return

    # получить информацию о паре

    await message.answer(
        "0.32462",
        reply_markup=keyboards.get_currency_kb()
    )
    await state.set_state(CurrencyStates.IN_CURRENCY)


async def get_analysis(message: types.Message, state: FSMContext):
    # формирование отчета
    await message.answer("Ваш отчет: ", reply_markup=keyboards.get_currency_kb())
    await state.set_state(CurrencyStates.IN_CURRENCY)


async def tracked_pares_handler(message: types.Message, state: FSMContext):
    await show_tracked_pares(message)
    await state.set_state(CurrencyStates.IN_TRACKED_PARES_LIST)


async def show_tracked_pares(message: types.Message):
    # получение списка отслеживаемых пар
    await message.answer("Ваш список отслеживаемых пар: ", reply_markup=keyboards.get_tracked_pares_kb())


async def add_new_tracked_pare_start(message: types.Message, state: FSMContext):
    await message.answer("Введите название новой пары: ", reply_markup=keyboards.get_back_kb())
    await state.set_state(CurrencyStates.WAITING_NEW_TRACKED_PARE_NAME)


async def add_new_tracked_pare_name(message: types.Message, state: FSMContext):
    if message.text == "назад":
        await state.clear()
        return

    # получить имя новой пары

    await message.answer("Новая пара добавлена", reply_markup=keyboards.get_tracked_pares_kb())
    await state.set_state(CurrencyStates.IN_TRACKED_PARES_LIST)


async def delete_tracked_pare_start(message: types.Message, state: FSMContext):
    await show_tracked_pares(message)
    await message.answer("Введите номер удаляемой пары: ", reply_markup=keyboards.get_back_kb())
    await state.set_state(CurrencyStates.WAITING_TRACKED_PARE_DELETE_NUMBER)


async def delete_tracked_pare_number(message: types.Message, state: FSMContext):
    if message.text == "назад":
        await state.clear()
        return

    # получение номера пары и удаление

    await message.answer("Пара удалена", reply_markup=keyboards.get_tracked_pares_kb())
    await state.set_state(CurrencyStates.IN_TRACKED_PARES_LIST)
