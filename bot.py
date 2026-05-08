import telebot
TOKEN = "8555000101:AAHK96VmhzJezBwceWSaXz1GinnHirb36rU"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, "Salom! Tanishuv botga xush kelibsiz!")

bot.polling()
