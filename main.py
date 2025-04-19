from dotenv import load_dotenv
import os
from handlers import BaseHandlers, SubscriptionHandlers, CategoryHandlers, SpendingsHandlers, CurrencyHandlers, \
    BinanceHandlers, AssetsReportHandlers
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
BASE_URL = os.getenv("BASE_URL")

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()


def register_handlers(dp):
    BaseHandlers.register_base_handlers(dp)
    SubscriptionHandlers.register_subscription_handlers(dp)
    CategoryHandlers.register_category_handlers(dp, BASE_URL)
    SpendingsHandlers.register_spendings_handlers(dp, BASE_URL)
    CurrencyHandlers.register_currency_handlers(dp, BASE_URL)
    AssetsReportHandlers.register_assets_report_handlers(dp, BASE_URL)


async def main():
    register_handlers(dp)
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
