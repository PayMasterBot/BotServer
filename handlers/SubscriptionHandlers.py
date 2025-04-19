from aiogram import F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards import keyboards
import aiohttp
import json

base_url=""

class SubscriptionStates(StatesGroup):
    IN_SUBSCRIPTIONS = State()
    WAITING_SUBSCR_NAME = State()
    WAITING_SUBSCR_PRICE = State()
    WAITING_SUBSCR_DELETE_NUMBER = State()


def register_subscription_handlers(dp, new_base_url):
    global base_url
    dp.message.register(subscriptions_handler, F.text == "подписки")
    dp.message.register(add_subscription_start, F.text == "добавить", SubscriptionStates.IN_SUBSCRIPTIONS)
    dp.message.register(delete_subscription_start, F.text == "удалить", SubscriptionStates.IN_SUBSCRIPTIONS)
    dp.message.register(add_subscription_name, SubscriptionStates.WAITING_SUBSCR_NAME)
    dp.message.register(add_subscription_price, SubscriptionStates.WAITING_SUBSCR_PRICE)
    dp.message.register(delete_subscription_number, SubscriptionStates.WAITING_SUBSCR_DELETE_NUMBER)
    base_url = new_base_url


async def show_subscriptions(message: types.Message):
    user_id = message.from_user.id
    request_url = base_url + "subscription"
    params = {
        "userId": user_id
    }

    text = ""
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(request_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    titles = [subscription["title"] for subscription in data]
                    text = "Ваши подписки:\n" + "\n".join(
                        f"{i + 1}. {titles[i]}"
                        for i in range(0, len(titles))
                    ) if titles else "У вас пока нет подписок."
                else:
                    text = "Произошла ошибка, попробуйте позже"
        except Exception as e:
            text = "Произошла ошибка подключения, попробуйте позже"

    await message.answer(text, reply_markup=keyboards.get_subscriptions_kb())


async def subscriptions_handler(message: types.Message, state: FSMContext):
    await state.set_state(SubscriptionStates.IN_SUBSCRIPTIONS)
    await show_subscriptions(message)


async def add_subscription_start(message: types.Message, state: FSMContext):
    await message.answer("Введите название подписки:", reply_markup=keyboards.get_back_kb())
    await state.set_state(SubscriptionStates.WAITING_SUBSCR_NAME)


async def add_subscription_name(message: types.Message, state: FSMContext):
    if message.text == "назад":
        await message.answer("Отмена добавления", reply_markup=keyboards.get_subscriptions_kb())
        await state.clear()
        return

    await state.update_data(name=message.text)
    await message.answer("Введите стоимость подписки в рублях:", reply_markup=keyboards.get_back_kb())
    await state.set_state(SubscriptionStates.WAITING_SUBSCR_PRICE)


async def add_subscription_price(message: types.Message, state: FSMContext):
    if message.text == "назад":
        await message.answer("Введите название подписки:", reply_markup=keyboards.get_back_kb())
        await state.clear()
        return

    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите число!")
        return

    data = await state.get_data()

    subscription_title = data['name']
    price = message.text
    user_id = message.from_user.id
    request_url = base_url + "subscription"
    params = {
        "userId": user_id
    }
    headers = {"Content-Type": "application/json"}
    payload = {
        "id": 0,
        "userId": 0,
        "title": subscription_title,
        "price": int(price)
    }

    text = ""

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(request_url, params=params, json=payload, headers=headers) as response:
                if response.status == 200:
                    text = "Подписка была добавлена!"
                else:
                    print(params, payload)
                    text = "Произошла ошибка добавления, попробуйте позже"
        except Exception as e:
            print(str(e))
            text = "Произошла ошибка подключения, попробуйте позже"

    await message.answer(text, reply_markup=keyboards.get_subscriptions_kb())
    await state.set_state(SubscriptionStates.IN_SUBSCRIPTIONS)


async def delete_subscription_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    request_url = base_url + "subscription"
    params = {
        "userId": user_id
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(request_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if len(data) == 0:
                        await message.answer("У вас нет подписок")
                        return
                else:
                    await message.answer("Произошла ошибка, попробуйте позже")
                    return
        except Exception as e:
            await message.answer("Произошла ошибка подключения, попробуйте позже")
            return

    await show_subscriptions(message)
    await message.answer("Введите номер подписки для удаления:", reply_markup=keyboards.get_back_kb())
    await state.set_state(SubscriptionStates.WAITING_SUBSCR_DELETE_NUMBER)


async def delete_subscription_number(message: types.Message, state: FSMContext):
    if message.text == "назад":
        await show_subscriptions(message)
        await state.clear()
        return

    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите номер!")
        return

    user_id = message.from_user.id
    subscription_index = int(message.text) - 1

    request_url = base_url + "subscription"
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

    if 0 <= subscription_index < len(data):
        request_url = base_url + "subscription/" + str(data[subscription_index]["id"])
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

    await message.answer("Подписка удалена", reply_markup=keyboards.get_subscriptions_kb())
    await state.set_state(SubscriptionStates.IN_SUBSCRIPTIONS)
