from aiogram import F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards import keyboards
from handlers import BaseHandlers
import aiohttp
import json

base_url=""

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
    # получить категории из БД
    category = ["Категория 1", "Категория 2", "Категория 3"]

    text = "Ваши категории:\n" + "\n".join(
        f"{i + 1}. {category[i]}"
        for i in range(0, len(category))
    ) if category else "У вас пока нет категорий."
    await message.answer(text, reply_markup=keyboards.get_back_kb())
    await message.answer("Введите порядковый номер категории:", reply_markup=keyboards.get_back_kb())
    await state.set_state(SpendingsStates.WAITING_SPENDING_CATEGORY)


async def new_spending_category(message: types.Message, state: FSMContext):
    if message.text == "назад":
        await message.answer("Отмена новой траты", reply_markup=keyboards.get_expenses_kb())
        await state.clear()
        return

    # добавить трату

    await message.answer(
        "Введите сумму траты",
        reply_markup=keyboards.get_back_kb()
    )
    await state.set_state(SpendingsStates.WAITING_SPENDING_COST)


async def new_spending_cost(message: types.Message, state: FSMContext):
    if message.text == "назад":
        await message.answer("Отмена новой траты", reply_markup=keyboards.get_expenses_kb())
        await state.clear()
        return

    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите номер!")
        return

    user_id = message.from_user.id
    num = int(message.text) - 1

    # добавление траты

    await message.answer("Трата добавлена", reply_markup=keyboards.get_expenses_kb())

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

    text = "Вот ваш сравнительный отчет "
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(request_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    text += str(data)
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

    text = "Вот ваш отчет за месяц "
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(request_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    text += str(data)
                else:
                    text = "Произошла ошибка, попробуйте позже"
        except Exception as e:
            text = "Произошла ошибка создания отчета, попробуйте позже"

    await message.answer(text, reply_markup=keyboards.get_spendings_analytics_kb())
