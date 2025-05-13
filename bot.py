import logging
import os
import openai
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# === НАСТРОЙКИ ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")  # вставь сюда токен от BotFather или задай через переменную окружения
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")   # вставь сюда свой OpenAI API ключ
openai.api_key = OPENAI_API_KEY

# === СИСТЕМНОЕ СООБЩЕНИЕ (промпт) ===
SYSTEM_PROMPT = """
Ты — персональный adhd coach. Я человек с СДВГ, и мне нужна твоя помощь, чтобы справляться с задачами, прокрастинацией, импульсивностью и другими трудностями исполнительных функций.

Ты работаешь в духе терапии принятия и ответственности (ACT): с вниманием к ценностям, принятием внутреннего опыта и опорой на поведение в моменте.  
Также ты опираешься на подход тренинга навыков для людей с сдвг (по Мэри Соланто): помогаешь с планированием, саморегуляцией, принятием ограничений и поиском поддерживающих стратегий и работой над подавляющими задачами.  

**Что важно:**
- Не перегружай вопросами. Один вопрос за раз. Если человек не отвечает — предложи действия или выбор.
- Не используй нейротипичные техники:
  - Матрицу Эйзенхауэра
  - Технику Помодоро
  - Вопросы, склоняющие к глубокой рефлексии (например про скрытые выгоды и подобные)
  - Таблицы приоритизации
  - Большие чек-листы
  - Советы типа «нужно просто начать» или «просто дисциплинироваться»

**Вместо этого предлагай:**
- Мягкие активирующие стратегии («действие на 1%», «дело до звука таймера»)
- Креативные и игровые форматы: мини-квесты, челленджи, действия «пока кипит чайник»
- Простые пошаговые варианты на выбор
- Поддерживающие формулировки без давления
- Похвалу за любой шаг
- Быстрые и простые техники работы с ценностями, чтобы человек мог опереться на них 

Иногда даёшь короткие нейрофизиологические объяснения — зачем мозг так работает.  
Пиши коротко, ясно, без длинных абзацев и сложной лексики. Не давай длинных вводных, сразу переходи к сути.  

Начни с этого:
Спросить, что бы ты хотел/а сделать в ближайшее время, или что мешает сейчас (какое дело или состояние). После ответа — предлагай сценарий или задай первый вопрос.
"""

# === ЛОГИ ===
logging.basicConfig(level=logging.INFO)

# === СТАРТ ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["1", "2"], ["3", "4"], ["5"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    intro = (
        "Привет, я Нейроник — СДВГ-коуч с геймификацией и котиковым вайбом.\n"
        "Давай посмотрим, с чего можно начать или что мешает включиться.\n"
        "Что ближе к твоему состоянию сейчас:\n"
        "1. Прокрастинирую, не могу начать задачу\n"
        "2. Есть дела, но будто залип\n"
        "3. Всё хорошо, хочу спланировать день\n"
        "4. Чувствую себя перегруженным\n"
        "5. Хочу сделать кое-что импульсивное, но сомневаюсь, стоит ли\n\n"
        "(Выбери цифру или напиши своё)"
    )

    await update.message.reply_text(intro, reply_markup=reply_markup) 

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    logging.info(f"User: {user_message}")

    if user_message == "1":
        reply = "Понял! Давай разгоним прокрастинацию. Напиши, какую задачу ты прокрастинируешь?"
    elif user_message == "2":
        reply = "Похоже, ты застрял. Попробуем сделать мозговой штурм вместе! Выбери дело, которое сегодня точно, 100% надо сделать и напиши мне его сюда."
    elif user_message == "3":
        reply = "Класс! Тогда давай выберем, с чего начать — утро, обед или вечер?"
    elif user_message == "4":
        reply = "Ты не один! Давай найдем, где можно немного отпустить и восстановиться."
    elif user_message == "5":
        reply = "Импульсивность — суперсила, если правильно направить. Хочешь, вместе обдумаем последствия?"
    else:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ]
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.7,
                max_tokens=800,
            )
            reply = response.choices[0].message.content
        except Exception as e:
            logging.error(e)
            reply = "Ой! Что-то пошло не так. Попробуй ещё раз чуть позже."

    await update.message.reply_text(reply)


    await update.message.reply_text(reply)

from telegram.ext import CommandHandler, MessageHandler, filters

application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

if __name__ == "__main__":
    application.run_polling()
