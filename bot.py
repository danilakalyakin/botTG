import logging
import openai
import random
from telegram import Bot
from apscheduler.schedulers.background import BackgroundScheduler
import time
import os
from flask import Flask
import threading

# ========== НАСТРОЙКИ ==========
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNELS = ['@repkdsmat', '@repkdsinf']

openai.api_key = OPENAI_API_KEY
bot = Bot(token=TELEGRAM_TOKEN)

# ========== СТИЛЬ ОБУЧЕНИЯ ==========
STYLE_MESSAGES = [
    {"role": "system", "content": "Ты опытный преподаватель математики и информатики. Пиши простые, полезные и понятные посты для школьников. Используй короткие предложения, понятные примеры, иногда эмодзи."},
    {"role": "user", "content": "ХОРОШО: Если вы видите √(x²), то это не просто x, а |x|. Это важно для ЕГЭ!"},
    {"role": "user", "content": "ПЛОХО: Математика — это великая наука. Её надо учить."},
]

TOPICS = [
    "квадратные уравнения", "производные", "простейшие графы", "тригонометрия",
    "системы уравнений", "параметры", "логика", "таблицы истинности", "основы Python"
]

# ========== ГЕНЕРАЦИЯ ПОСТА ==========
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

# ========== ОТПРАВКА ==========
def send_post():
    logging.info("Генерируется пост...")
    post = generate_post()
    if post:
        for channel in CHANNELS:
            try:
                bot.send_message(chat_id=channel, text=post)
                logging.info(f"Отправлено в {channel}")
                logging.info(f"Содержание:\n{post}")
            except Exception as e:
                logging.error(f"Ошибка отправки в {channel}: {e}")
    else:
        logging.warning("Пост не сгенерирован.")

# ========== ФЛАСК СЕРВЕР ==========
app = Flask(__name__)

@app.route('/')
def index():
    return "Бот работает"

def run_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_post, 'interval', seconds=10)
    scheduler.start()
    logging.info("Планировщик активирован")
    while True:
        time.sleep(10)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Запускаем планировщик в отдельном потоке
    threading.Thread(target=run_scheduler).start()

    # Запускаем фейковый веб-сервер
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
