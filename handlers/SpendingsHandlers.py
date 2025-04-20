from aiogram import F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards import keyboards
from handlers import BaseHandlers
from datetime import datetime, timezone
import aiohttp
import json

base_url = ""


class SpendingsStates(StatesGroup):
    SPENDINGS_ANALYTICS = State()
    WAITING_SPENDING_CATEGORY = State()
    WAITING_SPENDING_COST = State()


def register_spendings_handlers(dp, new_base_url):
    global base_url
    dp.message.register(new_spending_start, F.text == "новая трата")
    dp.message.register(new_spending_category, SpendingsStates.WAITING_SPENDING_CATEGORY)
    dp.message.register(new_spending_cost, SpendingsStates.WAITING_SPENDING_COST)
    dp.message.register(analysis_start, F.text == "анализ")
    dp.message.register(compare_analysis, F.text == "сравнить", SpendingsStates.SPENDINGS_ANALYTICS)
    dp.message.register(monthly_analysis, F.text == "за месяц", SpendingsStates.SPENDINGS_ANALYTICS)
    base_url = new_base_url


async def new_spending_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    request_url = base_url + "category"
    params = {
        "userId": user_id
    }

    text = "Ваши категории:\n"
    data = None
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(request_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    titles = [category["title"] for category in data]
                    for i in range(len(titles)):
                        text += str(i + 1) + ". " + titles[i] + "\n"
                    if titles:
                        text += "\nВведите порядковый номер категории"
                else:
                    text = "Произошла ошибка, или у вас пока нет категорий"
                    await message.answer(text, reply_markup=keyboards.get_expenses_kb())
                    return
        except Exception as e:
            text = "Произошла ошибка подключения, попробуйте позже"

    await message.answer(text, reply_markup=keyboards.get_back_kb())
    await state.set_state(SpendingsStates.WAITING_SPENDING_CATEGORY)
    if data:
        await state.update_data(custom_data=data)


async def new_spending_category(message: types.Message, state: FSMContext):
    if message.text == "назад":
        await message.answer("Отмена новой траты", reply_markup=keyboards.get_expenses_kb())
        await state.clear()
        return

    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите номер!")
        return

    category_index = int(message.text) - 1
    data = await state.get_data()
    data = data['custom_data']
    ids = [category["id"] for category in data]

    if 0 <= category_index < len(ids):
        await state.set_state(SpendingsStates.WAITING_SPENDING_COST)
        await state.update_data(custom_data=[data, category_index])
    else:
        await message.answer("Введите корректный номер для категории")
        return

    await message.answer("Введите сумму траты", reply_markup=keyboards.get_back_kb())


async def new_spending_cost(message: types.Message, state: FSMContext):
    if message.text == "назад":
        await message.answer("Отмена новой траты", reply_markup=keyboards.get_expenses_kb())
        await state.clear()
        return

    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите число!")
        return

    user_id = message.from_user.id
    price = int(message.text)
    data = await state.get_data()
    category_id = data['custom_data'][1]
    ids = [category["id"] for category in data['custom_data'][0]]
    titles = [category["title"] for category in data['custom_data'][0]]
    current_time = str(datetime.now(timezone.utc).isoformat(timespec='milliseconds'))
    plus_pos = current_time.find('+')
    current_time = current_time[0:plus_pos] + "Z"

    request_url = base_url + 'category/' + str(ids[category_id]) + '/spending'
    params = {
        "userId": user_id
    }
    headers = {"Content-Type": "application/json"}
    payload = {
        "userId": 0,
        "catId": 0,
        "date": current_time,
        "price": price,
        "title": titles[category_id]
    }

    text = ""

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(request_url, params=params, json=payload, headers=headers) as response:
                if response.status == 200:
                    text = "Трата была добавлена!"
                else:
                    print(response.status, request_url, payload)
                    text = "Произошла ошибка добавления, попробуйте позже"
        except Exception as e:
            print(str(e))
            text = "Произошла ошибка подключения, попробуйте позже"

    await message.answer(text, reply_markup=keyboards.get_expenses_kb())

    await state.set_state(BaseHandlers.BaseStates.IN_EXPENSES)


async def analysis_start(message: types.Message, state: FSMContext):
    await message.answer("Выберите вид анализа", reply_markup=keyboards.get_spendings_analytics_kb())
    await state.set_state(SpendingsStates.SPENDINGS_ANALYTICS)


async def compare_analysis(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    request_url = base_url + "category/report"
    params = {
        "userId": user_id
    }

    text = "Вот ваш сравнительный отчет:\n"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(request_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    text += "\nКатегории:\n"
                    for title in data.keys():
                        text += title + ": " + str(data[title]['prev_month']) + " рублей | " + str(
                            data[title]['cur_month']) + " рублей" + "\n"
                else:
                    text = "Произошла ошибка, попробуйте позже"
        except Exception as e:
            text = "Произошла ошибка создания отчета, попробуйте позже"

    await message.answer(text, reply_markup=keyboards.get_spendings_analytics_kb())


async def monthly_analysis(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    request_url = base_url + "category/report"
    params = {
        "userId": user_id
    }

    text = "Вот ваш отчет за месяц:\n"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(request_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    text += "\nКатегории:\n"
                    for title in data.keys():
                        text += title + ": " + str(data[title]['cur_month']) + " рублей" + "\n"
                else:
                    text = "Произошла ошибка, попробуйте позже"
        except Exception as e:
            print(str(e))
            text = "Произошла ошибка создания отчета, попробуйте позже"

    request_url = base_url + "subscription"
    params = {
        "userId": user_id
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(request_url, params=params) as response:
                if response.status == 200:
                    text += "\nПодписки:\n"
                    data = await response.json()
                    for index in range(len(data)):
                        text += data[index]["title"] + " " + str(data[index]["price"]) + " рублей" + "\n"
                else:
                    text = "Произошла ошибка, попробуйте позже"
        except Exception as e:
            text = "Произошла ошибка создания отчета, попробуйте позже"

    await message.answer(text, reply_markup=keyboards.get_spendings_analytics_kb())
