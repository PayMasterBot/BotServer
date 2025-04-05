from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import types


def build_keyboard(buttons: list[str], sizes: tuple[int] = (2,)):
    builder = ReplyKeyboardBuilder()
    for button in buttons:
        builder.add(types.KeyboardButton(text=button))
    builder.adjust(*sizes)
    return builder.as_markup(resize_keyboard=True)


def get_main_kb():
    return build_keyboard(["траты", "активы"], (1, 1))


def get_expenses_kb():
    return build_keyboard(["новая трата", "анализ", "подписки", "категории", "назад"], (2, 2, 1))


def get_subscriptions_kb():
    return build_keyboard(["добавить", "удалить", "назад"], (2, 1))


def get_category_kb():
    return build_keyboard(["добавить", "удалить", "назад"], (2, 1))


def get_back_kb():
    return build_keyboard(["назад"])
