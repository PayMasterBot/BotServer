from aiogram import F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards import keyboards
from handlers import BaseHandlers
import aiohttp
import json


base_url=""

class CurrencyStates(StatesGroup):
    IN_CURRENCY = State()
    WAITING_PARE_NAME = State()
    WAITING_NEW_TRACKED_PARE_NAME = State()
    WAITING_TRACKED_PARE_DELETE_NUMBER = State()
    IN_TRACKED_PARES_LIST = State()


def register_currency_handlers(dp, new_base_url):
    global base_url
    dp.message.register(currency_handler, F.text == "валюты")
    dp.message.register(get_pare_start, F.text == "запросить пару", CurrencyStates.IN_CURRENCY)
    dp.message.register(get_pare_name, CurrencyStates.WAITING_PARE_NAME)
    dp.message.register(get_analysis, F.text == "отчет", CurrencyStates.IN_CURRENCY)
    dp.message.register(tracked_pares_handler, F.text == "отслеживаемое", CurrencyStates.IN_CURRENCY)
    dp.message.register(add_new_tracked_pare_start, F.text == "добавить", CurrencyStates.IN_TRACKED_PARES_LIST)
    dp.message.register(add_new_tracked_pare_name, CurrencyStates.WAITING_NEW_TRACKED_PARE_NAME)
    dp.message.register(delete_tracked_pare_start, F.text == "удалить", CurrencyStates.IN_TRACKED_PARES_LIST)
    dp.message.register(delete_tracked_pare_number, CurrencyStates.WAITING_TRACKED_PARE_DELETE_NUMBER)
    base_url = new_base_url


async def currency_handler(message: types.Message, state: FSMContext):
    await message.answer("Валюты", reply_markup=keyboards.get_currency_kb())
    await state.set_state(CurrencyStates.IN_CURRENCY)


async def get_pare_start(message: types.Message, state: FSMContext):
    await message.answer("Введите название пары через пробел", reply_markup=keyboards.get_back_kb())
    await state.set_state(CurrencyStates.WAITING_PARE_NAME)


async def get_pare_name(message: types.Message, state: FSMContext):
    if message.text == "назад":
        await state.clear()
        return

    cur1, cur2 = message.text.split()
    request_url = base_url + "currency-pair/rate"
    params = {
        "Cur1": cur1,
        "Cur2": cur2
    }

    text = ""
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(request_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    print(data)
                    text = str(data)
                else:
                    text = "Произошла ошибка, проверьте название пары"
        except Exception as e:
            text = "Произошла ошибка подключения, попробуйте позже"

    await message.answer(text, reply_markup=keyboards.get_currency_kb())
    await state.set_state(CurrencyStates.IN_CURRENCY)


async def get_analysis(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    request_url = base_url + "currency-pair"
    params = {
        "userId": user_id
    }

    text = "Ваш отчет:\n"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(request_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()

                    for index in range(len(data)):
                        request_url = base_url + "currency-pair/rate"
                        params = {
                            "Cur1": data[index]["currency1"],
                            "Cur2": data[index]["currency2"]
                        }

                        async with aiohttp.ClientSession() as session:
                            try:
                                async with session.get(request_url, params=params) as response:
                                    if response.status == 200:
                                        rate_data = await response.json()
                                        print(rate_data)
                                        text += str(index + 1) + ". " + data[index]["currency1"] + "|" + \
                                                data[index]["currency2"] + "  " +str(rate_data) + "\n"
                                    else:
                                        text = "Произошла ошибка, попробуйте позже"
                                        await message.answer(text, reply_markup=keyboards.get_currency_kb())
                                        await state.set_state(CurrencyStates.IN_CURRENCY)
                                        return

                            except Exception as e:
                                print(str(e))
                                text = "Произошла ошибка подключения, попробуйте позже"
                                await message.answer(text, reply_markup=keyboards.get_currency_kb())
                                await state.set_state(CurrencyStates.IN_CURRENCY)
                                return
                else:
                    text = "Произошла ошибка, попробуйте позже"
        except Exception as e:
            print(str(e))
            text = "Произошла ошибка подключения, попробуйте позже"

    await message.answer(text, reply_markup=keyboards.get_currency_kb())
    await state.set_state(CurrencyStates.IN_CURRENCY)


async def tracked_pares_handler(message: types.Message, state: FSMContext):
    await show_tracked_pares(message)
    await state.set_state(CurrencyStates.IN_TRACKED_PARES_LIST)


async def show_tracked_pares(message: types.Message):
    user_id = message.from_user.id
    request_url = base_url + "currency-pair"
    params = {
        "userId": user_id
    }

    text = "Ваши отслеживаемые пары:\n"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(request_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    print(data)
                    for index in range(len(data)):
                        text += str(index + 1) + ". " + data[index]["currency1"] + "|" + data[index]["currency2"] + "\n"
                else:
                    text = "Произошла ошибка, либо список пуст"
        except Exception as e:
            text = "Произошла ошибка подключения, попробуйте позже"
    await message.answer(text, reply_markup=keyboards.get_tracked_pares_kb())


async def add_new_tracked_pare_start(message: types.Message, state: FSMContext):
    await message.answer("Введите название новой пары через проблем: ", reply_markup=keyboards.get_back_kb())
    await state.set_state(CurrencyStates.WAITING_NEW_TRACKED_PARE_NAME)


async def add_new_tracked_pare_name(message: types.Message, state: FSMContext):
    if message.text == "назад":
        await state.clear()
        return

    user_id = message.from_user.id
    cur1, cur2 = message.text.split()

    request_url = base_url + "currency-pair/rate"
    params = {
        "Cur1": cur1,
        "Cur2": cur2
    }

    text = ""
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(request_url, params=params) as response:
                if response.status == 200:
                    pass
                else:
                    text = "Проверьте название пары"
                    await message.answer(text, reply_markup=keyboards.get_tracked_pares_kb())
                    await state.set_state(CurrencyStates.IN_TRACKED_PARES_LIST)
                    return
        except Exception as e:
            text = "Произошла ошибка подключения, попробуйте позже"
            await message.answer(text, reply_markup=keyboards.get_tracked_pares_kb())
            await state.set_state(CurrencyStates.IN_TRACKED_PARES_LIST)
            return

    request_url = base_url + "currency-pair"
    params = {
        "userId": user_id
    }
    headers = {"Content-Type": "application/json"}
    payload = {
        "cur1": cur1,
        "cur2": cur2
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(request_url, params=params, json=payload, headers=headers) as response:
                if response.status == 200:
                    text = "Новая пара была добавлена!"
                else:
                    text = "Произошла ошибка добавления, может быть эта пара уже отслеживается"
        except Exception as e:
            print(str(e))
            text = "Произошла ошибка подключения, попробуйте позже"

    await message.answer(text, reply_markup=keyboards.get_tracked_pares_kb())
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
