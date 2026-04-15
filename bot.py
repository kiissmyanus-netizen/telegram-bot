import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

TOKEN = "8667480610:AAHtzhtHv8VFe1Ss6_gs0zuYrecivZse6EE"
ADMIN_ID = 7950739069

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ===== DATABASE =====
conn = sqlite3.connect("users.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    username TEXT,
    data TEXT
)
""")
conn.commit()

# ===== QUESTIONS =====
questions = [
    "Как вас зовут?",
    "Сколько вам лет?",
    "В какой стране вы проживаете?",
    "Есть ли у вас опыт работы? (если да — где?)",
    "Есть ли у вас ПК или ноутбук?",
    "Почему ушли с предыдущей работы?",
    "Готовы ли работать стабильно по графику?",
    "Зачем тебе эта работа?",
    "Сколько хочешь зарабатывать?",
    "Какая у тебя мечта или зачем тебе деньги?",
    "Что будешь делать, если нет результата первые дни?"
]

# ===== MEMORY =====
user_data = {}
user_step = {}

# ===== KEYBOARD =====
reset_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🔄 Начать заново")]],
    resize_keyboard=True
)

# ===== QUESTION SENDER =====
async def send_question(user_id):
    step = user_step[user_id]
    await bot.send_message(user_id, questions[step])


# ===== START =====
@dp.message(Command("start"))
async def start(message: types.Message):
    user_id = message.from_user.id

    user_data[user_id] = []
    user_step[user_id] = 0

    await message.answer(
        "👋 Привет!\n\n"
        "Заполни анкету, с тобой свяжутся в ближайшее время ✅"
    )

    await send_question(user_id)


# ===== RESET BUTTON =====
@dp.message(lambda message: message.text == "🔄 Начать заново")
async def restart(message: types.Message):
    user_id = message.from_user.id

    user_data[user_id] = []
    user_step[user_id] = 0

    await message.answer(
        "🔄 Начинаем заново...",
        reply_markup=ReplyKeyboardRemove()
    )

    await send_question(user_id)


# ===== MAIN HANDLER =====
@dp.message()
async def handler(message: types.Message):
    user_id = message.from_user.id
    user = message.from_user

    # защита если не начал анкету
    if user_id not in user_step:
        await message.answer("Нажми /start чтобы начать анкету")
        return

    user_data[user_id].append(message.text)
    user_step[user_id] += 1

    # ===== FINISH =====
    if user_step[user_id] >= len(questions):

        result = ""
        for q, a in zip(questions, user_data[user_id]):
            result += f"{q}\n➡️ {a}\n\n"

        username = f"@{user.username}" if user.username else "нет"

        final_text = (
            "🧾 НОВАЯ АНКЕТА\n\n"
            f"👤 Username: {username}\n\n"
            + result
        )

        # отправка админу
        await bot.send_message(ADMIN_ID, final_text)

        # сохранение в базу
        cursor.execute(
            "INSERT INTO applications (user_id, username, data) VALUES (?, ?, ?)",
            (user_id, username, result)
        )
        conn.commit()

        await message.answer(
            "✅ Анкета завершена!\nНажми кнопку чтобы начать заново.",
            reply_markup=reset_kb
        )

        # очистка
        user_data[user_id] = []
        user_step[user_id] = 0

    else:
        await send_question(user_id)


# ===== START BOT =====
async def main():
    print("BOT STARTED")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())