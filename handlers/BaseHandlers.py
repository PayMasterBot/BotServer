from aiogram import F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from keyboards import keyboards


def register_base_handlers(dp):
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(back_handler, F.text == "назад")
    dp.message.register(expenses_handler, F.text == "траты")


async def cmd_start(message: types.Message):
    await message.answer("Выберите раздел:", reply_markup=keyboards.get_main_kb())


async def back_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    await state.clear()

    if message.text == "подписки":
        from handlers.subscriptions import show_subscriptions
        await show_subscriptions(message)
    elif message.text in ["траты", "активы"]:
        await message.answer("Главное меню", reply_markup=keyboards.get_main_kb())
    else:
        await message.answer("Меню трат", reply_markup=keyboards.get_expenses_kb())


async def expenses_handler(message: types.Message):
    await message.answer("Раздел трат:", reply_markup=keyboards.get_expenses_kb())
