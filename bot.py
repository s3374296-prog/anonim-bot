import telebot
from telebot import types

TOKEN = "8555000101:AAHK96VmhzJezBwceWSaXz1GinnHirb36rU"
bot = telebot.TeleBot(TOKEN)

users = {}
searching = {}  # uid: True/False

def main_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🔍 Suhbatdosh qidirish")
    kb.add("🛑 Qidiruvni to'xtatish")
    return kb

def gender_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("Bola 🥷", "Qiz 🧕")
    return kb

# ───── /start ─────
@bot.message_handler(commands=['start'])
def start(m):
    uid = m.chat.id
    users.pop(uid, None)
    searching[uid] = False
    bot.send_message(uid, "Salom! Ismingizni kiriting:")
    bot.register_next_step_handler(m, get_name)

# ───── Ro'yxatdan o'tish ─────
def get_name(m):
    name = m.text.strip()
    if not name or name.startswith("/"):
        bot.send_message(m.chat.id, "Iltimos, ismingizni kiriting:")
        bot.register_next_step_handler(m, get_name)
        return
    users[m.chat.id] = {'name': name}
    bot.send_message(m.chat.id, f"Yaxshi, {name}! Yoshingizni kiriting:")
    bot.register_next_step_handler(m, get_age)

def get_age(m):
    text = m.text.strip()
    if not text.isdigit() or len(text) != 2:
        bot.send_message(m.chat.id, "❗ Yoshni to'g'ri kiriting (2 xonali son, masalan: 18):")
        bot.register_next_step_handler(m, get_age)
        return
    age = int(text)
    if age < 13 or age > 99:
        bot.send_message(m.chat.id, "❗ Yoshni to'g'ri kiriting (13-99 oralig'ida):")
        bot.register_next_step_handler(m, get_age)
        return
    users[m.chat.id]['age'] = age
    bot.send_message(m.chat.id, "Jinsingizni tanlang:", reply_markup=gender_kb())
    bot.register_next_step_handler(m, get_gender)

def get_gender(m):
    text = m.text.strip()
    if text not in ["Bola 🥷", "Qiz 🧕"]:
        bot.send_message(m.chat.id, "Iltimos, tugmalardan birini tanlang:", reply_markup=gender_kb())
        bot.register_next_step_handler(m, get_gender)
        return
    users[m.chat.id]['gender'] = text
    uid = m.chat.id
    p = users[uid]
    bot.send_message(
        uid,
        f"✅ Profil tayyor!\n\n"
        f"👤 Ism: {p['name']}\n"
        f"🎂 Yosh: {p['age']}\n"
        f"{'🥷' if 'Bola' in p['gender'] else '🧕'} Jins: {p['gender']}\n\n"
        f"Endi suhbatdosh qidirishingiz mumkin!",
        reply_markup=main_menu()
    )

# ───── Qidirish ─────
@bot.message_handler(func=lambda m: m.text == "🔍 Suhbatdosh qidirish")
def search(m):
    uid = m.chat.id
    if uid not in users or 'gender' not in users[uid]:
        bot.send_message(uid, "Avval ro'yxatdan o'ting: /start")
        return

    searching[uid] = True
    my_gender = users[uid]['gender']
    opposite = "Qiz 🧕" if "Bola" in my_gender else "Bola 🥷"

    found = None
    for oid, p in users.items():
        if oid == uid:
            continue
        if not searching.get(oid, False):
            continue
        if p.get('gender') == opposite:
            found = oid
            break

    if found:
        # Ikkalasini ham topildi deb belgilaymiz
        searching[uid] = False
        searching[found] = False

        p_me = users[uid]
        p_them = users[found]

        bot.send_message(
            uid,
            f"🎉 Suhbatdosh topildi!\n\n"
            f"👤 {p_them['name']}, {p_them['age']} yosh\n"
            f"{p_them['gender']}\n\n"
            f"Suhbatlashishni boshlang!",
            reply_markup=main_menu()
        )
        bot.send_message(
            found,
            f"🎉 Suhbatdosh topildi!\n\n"
            f"👤 {p_me['name']}, {p_me['age']} yosh\n"
            f"{p_me['gender']}\n\n"
            f"Suhbatlashishni boshlang!",
            reply_markup=main_menu()
        )
    else:
        bot.send_message(
            uid,
            "🔍 Suhbatdosh qidirilmoqda...\n"
            "To'xtatish uchun '🛑 Qidiruvni to'xtatish' tugmasini bosing.",
            reply_markup=main_menu()
        )

# ───── Qidiruvni to'xtatish ─────
@bot.message_handler(func=lambda m: m.text == "🛑 Qidiruvni to'xtatish")
def stop_search(m):
    uid = m.chat.id
    searching[uid] = False
    bot.send_message(uid, "🛑 Qidiruv to'xtatildi.", reply_markup=main_menu())

# ───── Boshqa xabarlar ─────
@bot.message_handler(func=lambda m: True)
def unknown(m):
    bot.send_message(m.chat.id, "Menyu tugmalaridan foydalaning.", reply_markup=main_menu())

bot.polling(none_stop=True)
    
