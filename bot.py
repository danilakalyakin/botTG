import logging
import openai
import random
from telegram import Bot
from apscheduler.schedulers.background import BackgroundScheduler
import time

# ========== НАСТРОЙКИ ==========
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

CHANNELS = ['@your_math_channel', '@your_inf_channel']  # Список каналов
POST_INTERVAL_HOURS = 2

openai.api_key = OPENAI_API_KEY
bot = Bot(token=TELEGRAM_TOKEN)

# ========== СТИЛЬ ОБУЧЕНИЯ ==========
STYLE_MESSAGES = [
    {"role": "system",
     "content": "Ты опытный преподаватель математики и информатики. Пиши простые, полезные и понятные посты для школьников. Используй короткие предложения, понятные примеры, иногда эмодзи."},
    {"role": "user", "content": "ХОРОШО: Если вы видите √(x²), то это не просто x, а |x|. Это важно для ЕГЭ!"},
    {"role": "user", "content": "ПЛОХО: Математика — это великая наука. Её надо учить."},
]

TOPICS = [
    "квадратные уравнения", "производные", "простейшие графы", "тригонометрия",
    "системы уравнений", "параметры", "логика", "таблицы истинности", "основы Python"
]


# ========== ФУНКЦИЯ ГЕНЕРАЦИИ ПОСТА ==========
def generate_post():
    topic = random.choice(TOPICS)
    prompt = f"Сделай короткий пост по теме: {topic} для подготовки к ЕГЭ/ОГЭ"
    messages = STYLE_MESSAGES + [{"role": "user", "content": prompt}]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7
        )
        content = response['choices'][0]['message']['content']
        return content
    except Exception as e:
        logging.error(f"Ошибка генерации: {e}")
        return None


# ========== ФУНКЦИЯ ОТПРАВКИ ==========
def send_post():
    post = generate_post()
    if post:
        for channel in CHANNELS:
            try:
                bot.send_message(chat_id=channel, text=post)
                logging.info(f"Отправлено в {channel}")
            except Exception as e:
                logging.error(f"Ошибка отправки в {channel}: {e}")
    else:
        logging.warning("Пост не сгенерирован.")


# ========== НАСТРОЙКА ПЛАНИРОВЩИКА ==========
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_post, 'interval', hours=POST_INTERVAL_HOURS)
    scheduler.start()

    logging.info("Бот запущен. Ожидание задач...")

    # Поддержание работы
    try:
        while True:
            time.sleep(10)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logging.info("Бот остановлен.")
