
import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from openai import OpenAI

# Configure logging
logging.basicConfig(level=logging.INFO)

# Bot token from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Initialize OpenRouter client
openrouter_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

# --- Handlers ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я бот для проверки ссылок и других ботов на мошенничество. Отправь мне ссылку или имя бота для проверки.")

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    help_text = (
        "Я могу помочь тебе проверить ссылки и других ботов на потенциальное мошенничество.\n\n"
        "*Как использовать:*\n"
        "1. Отправь мне подозрительную ссылку.\n"
        "2. Отправь мне имя пользователя (username) другого бота (например, `@scambot`).\n\n"
        "Я использую искусственный интеллект для анализа и предоставления информации. Помни, что мои ответы носят рекомендательный характер и не являются абсолютной гарантией безопасности.\n\n"
        "*Доступные команды:*\n"
        "/start - Начать взаимодействие\n"
        "/help - Показать это сообщение помощи"
    )
    await message.answer(help_text, parse_mode="Markdown")

@dp.message()
async def handle_message(message: types.Message):
    user_input = message.text
    logging.info(f"Получено сообщение от {message.from_user.id}: {user_input}")

    await message.answer("Проверяю... Пожалуйста, подождите.")

    try:
        # Use OpenRouter for AI analysis
        response = openrouter_client.chat.completions.create(
            model="openrouter/auto", # Using 'auto' to let OpenRouter select the best model
            messages=[
                {"role": "user", "content": f"Проверь следующую информацию на предмет мошенничества или скама. Если это ссылка, проанализируй ее на потенциальные угрозы (фишинг, вредоносное ПО). Если это имя бота, проанализируй его на признаки мошенничества (например, запросы личных данных, обещания легких денег). Ответь на русском языке, объяснив, почему это может быть скамом или почему это безопасно. Предоставь краткий и понятный ответ. Вот информация: {user_input}"}
            ]
        )
        ai_response = response.choices[0].message.content
        await message.answer(ai_response)

    except Exception as e:
        logging.error(f"Ошибка при обращении к OpenRouter API: {e}")
        await message.answer("Извините, произошла ошибка при проверке. Пожалуйста, попробуйте еще раз позже.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
