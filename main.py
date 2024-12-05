import asyncio
import logging
import sys
import json
from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, FSInputFile

# Токен бота
TOKEN = getenv("BOT_TOKEN")
ADMIN_ID = getenv("ADMIN_ID")  # Замените на ваш Telegram ID

# Путь к файлу для хранения кликов
DATA_FILE = "click_data.json"

# Инициализация диспетчера
dp = Dispatcher()


# Загрузка и сохранение данных
def load_data():
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"click_count": 0, "user_list": []}


def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file)


# Загрузка текущего состояния
data = load_data()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    Обработчик команды /start
    """
    global data
    # Сообщение пользователю
    user_message = (
        "⚠️ На данный момент наши мощности не позволяют принять в работу новых пользователей.\n"
        "📌 Но мы обязательно оповестим вас, когда решим эту небольшую техническую неполадку!\n\n"
        "✨ Спасибо за ваше терпение и интерес к нашим услугам!"
    )
    await message.answer(user_message)
    user_id = message.from_user.id
    # Увеличение счетчика и сохранение данных
    if user_id not in data["user_list"]:
        data["user_list"].append(user_id)
        data["click_count"] += 1
        save_data(data)

        # Уведомление админа
        if data["click_count"] % 2 == 0:
            await message.bot.send_message(ADMIN_ID, f"На /start нажали {data['click_count']} раз(а).")
        if data["click_count"] % 10 == 0:
            try:
                file = FSInputFile(DATA_FILE)
                await message.bot.send_document(chat_id=ADMIN_ID, document=file,
                                                caption="📄 Новые данные по пользователям.")
            except Exception as e:
                await message.answer(f"Ошибка при отправке файла: {e}")


async def main() -> None:
    # Инициализация бота
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # Запуск бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
