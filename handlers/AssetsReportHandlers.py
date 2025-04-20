from aiogram import F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from handlers import BaseHandlers
from keyboards import keyboards
import aiohttp
import json

base_url = ""


def register_assets_report_handlers(dp, new_base_url):
    global base_url
    dp.message.register(get_analysis, F.text == "отчет", BaseHandlers.BaseStates.IN_ASSETS)
    base_url = new_base_url


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
                    if len(data) == 0:
                        text = "Список отслеживаемых пар пуст"
                    else:
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
                                                    data[index]["currency2"] + "  " + str(rate_data) + "\n"
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
                    text = "Произошла ошибка, возможно список отслеживаемых пар пуст"
        except Exception as e:
            print(str(e))
            text = "Произошла ошибка подключения, попробуйте позже"

    await message.answer(text, reply_markup=keyboards.get_assets_kb())
    await state.set_state(BaseHandlers.BaseStates.IN_ASSETS)
