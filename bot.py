import telebot
from telebot import types

TOKEN = "8555000101:AAHK96VmhzJezBwceWSaXz1GinnHirb36rU"
bot = telebot.TeleBot(TOKEN)

users = {}
likes = {}
matches = {}

def main_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("💕 Qidirish", "✏️ Profilim")
    kb.add("💌 Matchlar", "ℹ️ Yordam")
    return kb

def gender_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("👨 Erkak", "👩 Ayol")
    return kb

@bot.message_handler(commands=['start'])
def start(m):
    if m.chat.id in users:
        bot.send_message(m.chat.id, f"Xush kelibsiz, {users[m.chat.id]['name']}!", reply_markup=main_menu())
    else:
        bot.send_message(m.chat.id, "Salom! Ismingizni kiriting:")
        bot.register_next_step_handler(m, get_name)

def get_name(m):
    users[m.chat.id] = {'name': m.text}
    bot.send_message(m.chat.id, "Yoshingizni kiriting:")
    bot.register_next_step_handler(m, get_age)

def get_age(m):
    users[m.chat.id]['age'] = m.text
    bot.send_message(m.chat.id, "Jinsingiz:", reply_markup=gender_kb())
    bot.register_next_step_handler(m, get_gender)

def get_gender(m):
    users[m.chat.id]['gender'] = m.text
    bot.send_message(m.chat.id, "Shahringiz:", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(m, get_city)

def get_city(m):
    users[m.chat.id]['city'] = m.text
    bot.send_message(m.chat.id, "O'zingiz haqida yozing:")
    bot.register_next_step_handler(m, get_about)

def get_about(m):
    users[m.chat.id]['about'] = m.text
    bot.send_message(m.chat.id, "Rasmingizni yuboring:")
    bot.register_next_step_handler(m, get_photo)

def get_photo(m):
    if m.photo:
        users[m.chat.id]['photo'] = m.photo[-1].file_id
        bot.send_message(m.chat.id, "Profil yaratildi!", reply_markup=main_menu())
    else:
        bot.send_message(m.chat.id, "Rasm yuboring!")
        bot.register_next_step_handler(m, get_photo)

@bot.message_handler(func=lambda m: m.text == "💕 Qidirish")
def search(m):
    uid = m.chat.id
    found = None
    for oid, p in users.items():
        if oid == uid:
            continue
        if oid in likes.get(uid, []):
            continue
        if 'photo' not in p:
            continue
        found = (oid, p)
        break
    if found:
        oid, p = found
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("❤️", callback_data=f"like_{oid}"),
               types.InlineKeyboardButton("👎", callback_data=f"skip_{oid}"))
        bot.send_photo(uid, p['photo'],
            caption=f"👤 {p['name']}, {p['age']}\n🏙 {p['city']}\n📝 {p['about']}",
            reply_markup=kb)
    else:
        bot.send_message(uid, "Hozircha yangi profil yo'q.")

@bot.callback_query_handler(func=lambda c: c.data.startswith("like_") or c.data.startswith("skip_"))
def handle_like(c):
    uid = c.message.chat.id
    action, oid = c.data.split("_")
    oid = int(oid)
    if uid not in likes:
        likes[uid] = []
    likes[uid].append(oid)
    if action == "like" and uid in likes.get(oid, []):
        if uid not in matches:
            matches[uid] = []
        if oid not in matches:
            matches[oid] = []
        matches[uid].append(oid)
        matches[oid].append(uid)
        bot.answer_callback_query(c.id, "MATCH!")
        uname = users[oid].get('username', '')
        bot.send_message(uid, f"Match! {users[oid]['name']} bilan tanishdingiz!")
        bot.send_message(oid, f"Match! {users[uid]['name']} sizni yoqtirdi!")
    else:
        bot.answer_callback_query(c.id)
    bot.delete_message(uid, c.message.message_id)
    search_next(uid)

def search_next(uid):
    class Fake:
        chat = type('c', (), {'id': uid})()
        text = "💕 Qidirish"
    search(Fake())

@bot.message_handler(func=lambda m: m.text == "✏️ Profilim")
def my_profile(m):
    uid = m.chat.id
    if uid not in users or 'photo' not in users[uid]:
        bot.send_message(uid, "Profil yo'q. /start")
        return
    p = users[uid]
    bot.send_photo(uid, p['photo'],
        caption=f"👤 {p['name']}, {p['age']}\n🏙 {p['city']}\n📝 {p['about']}")

@bot.message_handler(func=lambda m: m.text == "💌 Matchlar")
def my_matches(m):
    uid = m.chat.id
    ms = matches.get(uid, [])
    if not ms:
        bot.send_message(uid, "Hali matchlar yo'q.")
        return
    bot.send_message(uid, f"Sizda {len(ms)} ta match bor!")

@bot.message_handler(func=lambda m: m.text == "ℹ️ Yordam")
def help_msg(m):
    bot.send_message(m.chat.id, "💕 Qidirish - profillarni ko'ring\n❤️ Like bosing - match bo'lsa xabar keladi!")

bot.polling()
