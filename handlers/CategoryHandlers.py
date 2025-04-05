from aiogram import F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards import keyboards


class CategoryStates(StatesGroup):
    IN_CATEGORY = State()
    WAITING_CATEGORY_NAME = State()
    WAITING_CATEGORY_DELETE_NUMBER = State()


def register_category_handlers(dp):
    dp.message.register(category_handler, F.text == "категории")
    dp.message.register(add_category_start, F.text == "добавить", CategoryStates.IN_CATEGORY)
    dp.message.register(delete_category_start, F.text == "удалить", CategoryStates.IN_CATEGORY)
    dp.message.register(add_category_name, CategoryStates.WAITING_CATEGORY_NAME)
    dp.message.register(delete_category_number, CategoryStates.WAITING_CATEGORY_DELETE_NUMBER)


async def show_category(message: types.Message):
    # user_id = message.from_user.id
    # получить категории из БД
    category = ["Категория 1", "Категория 2", "Категория 3"]

    text = "Ваши категории:\n" + "\n".join(
        f"{i + 1}. {category[i]}"
        for i in range(0, len(category))
    ) if category else "У вас пока нет категорий."
    await message.answer(text, reply_markup=keyboards.get_category_kb())


async def category_handler(message: types.Message, state: FSMContext):
    await state.set_state(CategoryStates.IN_CATEGORY)
    await show_category(message)


async def add_category_start(message: types.Message, state: FSMContext):
    await message.answer("Введите название Категории:", reply_markup=keyboards.get_back_kb())
    await state.set_state(CategoryStates.WAITING_CATEGORY_NAME)


async def add_category_name(message: types.Message, state: FSMContext):
    if message.text == "назад":
        await message.answer("Отмена добавления", reply_markup=keyboards.get_category_kb())
        await state.clear()
        return

    data = await state.get_data()
    user_id = message.from_user.id

    # добавить категорию

    await message.answer(
        f"Категория добавлена!",
        reply_markup=keyboards.get_category_kb()
    )
    await state.set_state(CategoryStates.IN_CATEGORY)


async def delete_category_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    # проверка на наличие категорий

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
    num = int(message.text) - 1

    # удаление категории
    await message.answer("Категория удалена", reply_markup=keyboards.get_category_kb())

    await state.set_state(CategoryStates.IN_CATEGORY)
