import asyncio
import logging
import os

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from keyboards.commands import set_commands
from config.logging import setup_logging
from utils.exceptions import HomeworkBotError
from database.init import init_db
from handlers.register import router as register_router
from handlers.start import router as start_router
from handlers.timer import setup_timer_handlers, scheduler
from handlers.about import setup_about_handlers

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_ADMIN_ID = os.getenv('TELEGRAM_ADMIN_ID')

dp = Dispatcher()
dp.include_router(register_router)
dp.include_router(start_router)


def check_tokens():
    """Проверяет наличие всех необходимых токенов."""
    missing_tokens = [
        token for token, value in {
            'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
        }.items() if not value
    ]
    if missing_tokens:
        logging.critical(f'Отсутствуют токены: {", ".join(missing_tokens)}')
        return False
    return True


async def on_startup(bot: Bot):
    """Действия при запуске бота"""
    await set_commands(bot)
    setup_timer_handlers(dp)
    setup_about_handlers(dp)
    scheduler.start()
    try:
        await bot.send_message(TELEGRAM_ADMIN_ID, text='Бот запущен')
    except HomeworkBotError as e:
        logging.error(f"Ошибка бота: {str(e)}")


async def on_shutdown():
    """Действия при остановке бота"""
    scheduler.shutdown()

dp.startup.register(on_startup)
dp.shutdown.register(on_shutdown)


async def main() -> None:
    if not check_tokens():
        exit()

    init_db()
    bot = Bot(
        token=TELEGRAM_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        setup_logging()
        logging.info("="*50)
        logging.info("Запуск бота")
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.warning("Бот остановлен")
    except Exception as e:
        logging.error(f"Ошибка: {str(e)}", exc_info=True)
    finally:
        logging.info("Работа завершена")
