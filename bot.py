import json
import time
import os
import logging
import openai
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# === НАСТРОЙКИ ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")  # вставь сюда токен от BotFather или задай через переменную окружения
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")   # вставь сюда свой OpenAI API ключ
client = openai.OpenAI(api_key=OPENAI_API_KEY)

MEMORY_FILE = "memory.json"
MEMORY_LIFETIME = 86400  # 24 часа в секундах

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {}
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return {}
    now = time.time()
    return {
        uid: [msg for msg in history if now - msg["ts"] < MEMORY_LIFETIME]
        for uid, history in data.items()
    }

def save_memory(memory):
    serializable = {
        uid: [{"ts": msg.get("ts", time.time()), "role": msg["role"], "content": msg["content"]}
              for msg in history]
        for uid, history in memory.items()
    }
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(serializable, f, ensure_ascii=False, indent=2)

# === СИСТЕМНОЕ СООБЩЕНИЕ (промпт) ===
SYSTEM_PROMPT = """
Ты — персональный adhd coach. Я человек с СДВГ, и мне нужна твоя помощь, чтобы справляться с задачами, прокрастинацией, импульсивностью и другими трудностями исполнительных функций.

Ты работаешь в духе терапии принятия и ответственности (ACT): с вниманием к ценностям, принятием внутреннего опыта и опорой на поведение в моменте.
Также ты опираешься на подход тренинга навыков для людей с СДВГ (по Мэри Соланто): помогаешь с планированием, саморегуляцией, принятием ограничений и поиском поддерживающих стратегий, а также с работой над подавляющими задачами.

Важно: Никогда не задавай более одного вопроса за раз. Один вопрос — одно сообщение. Даже если очень хочется задать уточняющий или связанный вопрос — дождись ответа, прежде чем продолжать.

Если человек не отвечает — предложи лёгкое действие или два простых варианта на выбор.
Не используй нейротипичные техники:
  Матрицу Эйзенхауэра
  Технику Помодоро
  Глубокую рефлексию (вопросы про скрытые выгоды и т.п.)
  Таблицы и большие чек-листы
  Советы вроде «просто начни» или «надо быть дисциплинированным»

Вместо этого используй:
  Мягкие активирующие стратегии (например, «действие на 1%», «сделай пока закипает чайник», «до звука таймера»)
  Креативные и игровые форматы: мини-квесты, микро-челленджи
  Простые пошаговые варианты с выбором
  Поддерживающие, доброжелательные формулировки без давления
  Сенсорные или телесные способы активации
  Похвалу даже за самый маленький шаг
  Короткие и простые техники работы с ценностями
  Ты также можешь кратко объяснять нейрофизиологию — как работает мозг при СДВГ, какие особенности есть в регуляции нейромедиаторов и исполнительных функций. Пиши ясно, коротко, без сложной лексики. Не давай длинных абзацев — только по сути.

Начни с этого:
  Спроси, что человек хотел бы сделать в ближайшее время или что сейчас мешает (задача или состояние).
После ответа — предложи сценарий или задай один следующий вопрос.

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
  
def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {}
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return {}
    now = time.time()
    return {
        uid: [msg for msg in history if now - msg["ts"] < MEMORY_LIFETIME]
        for uid, history in data.items()
    }

def save_memory(memory):
    serializable = {
        uid: [{"role": m["role"], "content": m["content"], "ts": m["ts"]} for m in history]
        for uid, history in memory.items()
    }
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(serializable, f, ensure_ascii=False, indent=2)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_message = update.message.text
    logging.info(f"User {user_id}: {user_message}")

    memory = load_memory()
    user_history = memory.get(user_id, [])

    # Добавляем сообщение пользователя
    user_history.append({
        "role": "user",
        "content": user_message,
        "ts": time.time()
    })

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
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + [
            {"role": m["role"], "content": m["content"]} for m in user_history
        ]

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.7,
                max_tokens=800,
            )
            reply = response.choices[0].message.content
        except Exception as e:
            logging.error(f"OpenAI error: {e}")
            await update.message.reply_text("⚠️ Ой! Что-то пошло не так. Попробуй ещё раз чуть позже.")
            return

        user_history.append({
            "role": "assistant",
            "content": reply,
            "ts": time.time()
        })

    memory[user_id] = user_history
    save_memory(memory)

    await update.message.reply_text(reply)

from telegram.ext import CommandHandler, MessageHandler, filters

application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

if __name__ == "__main__":
    application.run_polling()
