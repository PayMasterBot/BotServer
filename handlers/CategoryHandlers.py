from aiogram import F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import requests
import aiohttp
import json
from keyboards import keyboards

base_url = ""


class CategoryStates(StatesGroup):
    IN_CATEGORY = State()
    WAITING_CATEGORY_NAME = State()
    WAITING_CATEGORY_DELETE_NUMBER = State()


def register_category_handlers(dp, new_base_url):
    global base_url
    dp.message.register(category_handler, F.text == "категории")
    dp.message.register(add_category_start, F.text == "добавить", CategoryStates.IN_CATEGORY)
    dp.message.register(delete_category_start, F.text == "удалить", CategoryStates.IN_CATEGORY)
    dp.message.register(add_category_name, CategoryStates.WAITING_CATEGORY_NAME)
    dp.message.register(delete_category_number, CategoryStates.WAITING_CATEGORY_DELETE_NUMBER)
    base_url = new_base_url


async def show_category(message: types.Message):
    user_id = message.from_user.id
    request_url = base_url + "category"
    params = {
        "userId": user_id
    }

    text = "Ваши категории:\n"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(request_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    titles = [category["title"] for category in data]
                    for i in range(len(titles)):
                        text += str(i + 1) + ". " + titles[i] + "\n"
                else:
                    text = "Произошла ошибка, или у вас пока нет категорий"
        except Exception as e:
            text = "Произошла ошибка подключения, попробуйте позже"

    await message.answer(text, reply_markup=keyboards.get_category_kb())


async def category_handler(message: types.Message, state: FSMContext):
    await state.set_state(CategoryStates.IN_CATEGORY)
    await show_category(message)


async def add_category_start(message: types.Message, state: FSMContext):
    await message.answer("Введите название категории:", reply_markup=keyboards.get_back_kb())
    await state.set_state(CategoryStates.WAITING_CATEGORY_NAME)


async def add_category_name(message: types.Message, state: FSMContext):
    if message.text == "назад":
        await message.answer("Отмена добавления", reply_markup=keyboards.get_category_kb())
        await state.clear()
        return

    category_title = message.text
    user_id = message.from_user.id
    request_url = base_url + "category"
    params = {
        "userId": user_id
    }

    text = "Ваши категории:\n"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(request_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    titles = [category["title"] for category in data]
                    if category_title in titles:
                        text = "Такая категория уже есть"
                        await message.answer(text, reply_markup=keyboards.get_back_kb())
                        return
                else:
                    pass
        except Exception as e:
            pass

    request_url = base_url + "category"
    params = {
        "userId": user_id
    }
    headers = {"Content-Type": "application/json"}
    payload = {
        "id": 0,
        "title": category_title
    }

    text = ""

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(request_url, params=params, json=payload, headers=headers) as response:
                if response.status == 200:
                    text = "Категория была добавлена!"
                else:
                    print(response.status)
                    text = "Произошла ошибка добавления, попробуйте позже"
        except Exception as e:
            print(str(e))
            text = "Произошла ошибка подключения, попробуйте позже"

    await message.answer(
        text,
        reply_markup=keyboards.get_category_kb()
    )
    await state.set_state(CategoryStates.IN_CATEGORY)


async def delete_category_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    request_url = base_url + "category"
    params = {
        "userId": user_id
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(request_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    titles = [category["title"] for category in data]
                    if len(titles) == 0:
                        await message.answer("У вас нет категорий")
                        return
                else:
                    await message.answer("Произошла ошибка, попробуйте позже")
                    return
        except Exception as e:
            await message.answer("Произошла ошибка подключения, попробуйте позже")
            return

    await show_category(message)
    await message.answer("Введите номер категории для удаления:", reply_markup=keyboards.get_back_kb())
    await state.set_state(CategoryStates.WAITING_CATEGORY_DELETE_NUMBER)


async def delete_category_number(message: types.Message, state: FSMContext):
    if message.text == "назад":
        await show_category(message)
        await state.clear()
        return

    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите номер!")
        return

    user_id = message.from_user.id
    category_index = int(message.text) - 1

    request_url = base_url + "category"
    params = {
        "userId": user_id
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(request_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                else:
                    await message.answer("Произошла ошибка, попробуйте позже")
                    return
        except Exception as e:
            await message.answer("Произошла ошибка подключения, попробуйте позже")
            return
    ids = [category["id"] for category in data]
    if 0 <= category_index < len(ids):
        request_url = base_url + "category/" + str(ids[category_index])
        params = {
            "userId": user_id
        }
        async with aiohttp.ClientSession() as session:
            try:
                async with session.delete(request_url, params=params) as response:
                    if response.status == 200:
                        pass
                    else:
                        await message.answer("Произошла ошибка, попробуйте позже")
                        return
            except Exception as e:
                await message.answer("Произошла ошибка подключения, попробуйте позже")
                return
    else:
        await message.answer("Введите корректный номер для удаления")
        return

    await message.answer("Категория удалена", reply_markup=keyboards.get_category_kb())

    await state.set_state(CategoryStates.IN_CATEGORY)
