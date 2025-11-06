import telebot
import os

# توکن رو بعداً می‌ذاریم، اینجا فقط می‌خونیم
bot = telebot.TeleBot(os.environ['TOKEN'])

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "سلام داداش! من ۲۴ ساعته آنلاینم! 🚀")

@bot.message_handler(func=lambda m: True)
def echo(message):
    bot.reply_to(message, f"تو گفتی: {message.text}")

print("ربات داره ران می‌شه...")
bot.infinity_polling()
