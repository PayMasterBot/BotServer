from aiogram import F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from handlers import BaseHandlers
from keyboards import keyboards


def register_assets_report_handlers(dp):
    dp.message.register(get_analysis, F.text == "отчет", BaseHandlers.BaseStates.IN_ASSETS)


async def get_analysis(message: types.Message, state: FSMContext):
    # сформировать отчет
    await message.answer("Ваш отчет:", reply_markup=keyboards.get_assets_kb())
    await state.set_state(BaseHandlers.BaseStates.IN_ASSETS)
