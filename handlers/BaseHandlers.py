from aiogram import F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards import keyboards
from handlers import SubscriptionHandlers


class BaseStates(StatesGroup):
    IN_EXPENSES = State()
    IN_ASSETS = State()
    IN_MAIN = State()


def register_base_handlers(dp):
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(back_handler, F.text == "назад")
    dp.message.register(expenses_handler, F.text == "траты")


async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer("Выберите раздел:", reply_markup=keyboards.get_main_kb())
    await state.set_state(BaseStates.IN_MAIN)


async def back_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    await state.clear()

    if current_state == SubscriptionHandlers.SubscriptionStates.WAITING_NAME.state or \
            current_state == SubscriptionHandlers.SubscriptionStates.WAITING_PRICE.state or \
            current_state == SubscriptionHandlers.SubscriptionStates.WAITING_DELETE_NUMBER.state:
        await SubscriptionHandlers.show_subscriptions(message)

    elif message.text == "подписки":
        await SubscriptionHandlers.show_subscriptions(message)

    elif current_state == BaseStates.IN_EXPENSES or current_state == BaseStates.IN_ASSETS:
        await message.answer("Главное меню", reply_markup=keyboards.get_main_kb())
        await state.set_state(BaseStates.IN_MAIN)

    else:
        await message.answer("Меню трат", reply_markup=keyboards.get_expenses_kb())
        await state.set_state(BaseStates.IN_EXPENSES)


async def expenses_handler(message: types.Message, state: FSMContext):
    await message.answer("Раздел трат:", reply_markup=keyboards.get_expenses_kb())
    await state.set_state(BaseStates.IN_EXPENSES)
