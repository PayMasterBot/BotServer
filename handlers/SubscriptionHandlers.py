from aiogram import F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards import keyboards


class SubscriptionStates(StatesGroup):
    IN_SUBSCRIPTIONS = State()
    WAITING_SUBSCR_NAME = State()
    WAITING_SUBSCR_PRICE = State()
    WAITING_SUBSCR_DELETE_NUMBER = State()


def register_subscription_handlers(dp):
    dp.message.register(subscriptions_handler, F.text == "подписки")
    dp.message.register(add_subscription_start, F.text == "добавить", SubscriptionStates.IN_SUBSCRIPTIONS)
    dp.message.register(delete_subscription_start, F.text == "удалить", SubscriptionStates.IN_SUBSCRIPTIONS)
    dp.message.register(add_subscription_name, SubscriptionStates.WAITING_SUBSCR_NAME)
    dp.message.register(add_subscription_price, SubscriptionStates.WAITING_SUBSCR_PRICE)
    dp.message.register(delete_subscription_number, SubscriptionStates.WAITING_SUBSCR_DELETE_NUMBER)


async def show_subscriptions(message: types.Message):
    # user_id = message.from_user.id
    # получить подписки из БД
    subscriptions = [{"name": "Подписка 1", "price": "100"}, {"name": "Подписка 2", "price": "200"}]

    text = "Ваши подписки:\n" + "\n".join(
        f"{i + 1}. {sub['name']} - {sub['price']} руб."
        for i, sub in enumerate(subscriptions)
    ) if subscriptions else "У вас пока нет подписок."

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
    user_id = message.from_user.id

    # добавить подписку

    await message.answer(
        f"Подписка '{data['name']}' за {message.text} руб. добавлена!",
        reply_markup=keyboards.get_subscriptions_kb()
    )
    await state.set_state(SubscriptionStates.IN_SUBSCRIPTIONS)


async def delete_subscription_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    # проверка на наличие подписок

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
    num = int(message.text) - 1

    # удаление подписки
    await message.answer("Подписка удалена", reply_markup=keyboards.get_subscriptions_kb())

    await state.set_state(SubscriptionStates.IN_SUBSCRIPTIONS)
