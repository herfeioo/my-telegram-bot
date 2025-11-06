import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import os

# توکن رو از Render می‌خونه (مخفی!)
TOKEN = os.environ['BOT_TOKEN']
CHANNEL_ID = "@tiza_film"
INSTAGRAM_LINK = "https://instagram.com/tiza_film"

films = {
    "film20251016": "https://t.me/+Q-PdZ7e9VOw2ZTdk",
    "film5": "https://t.me/+BNQRqgYdbH4zMWM0",
    "film6": "https://t.me/+xfrlh6ufRIc5MWRk",
    "film7": "https://t.me/+0qRfE0EsSuA3MDZk",
    "film8": "https://t.me/+B0C24RbzjFVjNTM0",
}

user_film_count = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = context.args
    if not args:
        welcome_text = (
            f"درود بر شما! 🎬 خوش آمدی به دنیای جذاب تیزا فیلم!\n\n"
            f"برای دیدن سکانس فیلم‌ها، وارد اینستاگرام ما شو:\n{INSTAGRAM_LINK}\n\n"
            f"برای دانلود فیلم‌ها و لینک تلگرام اصلی، روی دکمه زیر کلیک کن."
        )
        keyboard_welcome = InlineKeyboardMarkup([
            [InlineKeyboardButton("تلگرام اصلی", url=f"https://t.me/{CHANNEL_ID.strip('@')}")]
        ])
        welcome_msg = await update.message.reply_text(welcome_text, reply_markup=keyboard_welcome)
        asyncio.create_task(delete_message_later(context.bot, welcome_msg.chat.id, welcome_msg.message_id, 200))
        return

    film_code = args[0]
    if film_code not in films:
        err_msg = await update.message.reply_text("❌ فیلم پیدا نشد! لطفاً کد صحیح فیلم را ارسال کنید.")
        asyncio.create_task(delete_message_later(context.bot, err_msg.chat.id, err_msg.message_id, 200))
        return
    await check_membership(update, context, film_code)

async def check_membership(update_obj, context, film_code):
    user = update_obj.effective_user
    try:
        member = await context.bot.get_chat_member(CHANNEL_ID, user.id)
        if member.status in ["left", "kicked"]:
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("جوین کانال", url=f"https://t.me/{CHANNEL_ID.strip('@')}")],
                [InlineKeyboardButton("جوین شدم", callback_data=f"check_{film_code}")]
            ])
            not_member_msg = await update_obj.message.reply_text(
                "⚠️ هنوز عضو کانال نشده‌ای! لطفاً ابتدا روی جوین کانال بزن و بعد دکمه جوین شدم را فشار بده.",
                reply_markup=keyboard
            )
            asyncio.create_task(delete_message_later(context.bot, not_member_msg.chat.id, not_member_msg.message_id, 200))
            return
    except Exception as e:
        print(f"Error checking membership: {e}")
        return
    await send_film_link(update_obj, film_code)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    if query.data.startswith("check_"):
        film_code = query.data.split("_")[1]
        try:
            member = await context.bot.get_chat_member(CHANNEL_ID, user.id)
            if member.status in ["left", "kicked"]:
                await query.edit_message_text(
                    "🚫 هنوز عضو کانال نشدی! ابتدا روی جوین کانال بزن و دوباره جوین شدم را فشار بده."
                )
                return
        except:
            return
        await send_film_link(query, film_code)

async def send_film_link(update_obj, film_code):
    user_id = update_obj.effective_user.id if hasattr(update_obj, 'effective_user') else update_obj.from_user.id
    link = films[film_code]
    count = user_film_count.get((user_id, film_code), 0)
    if count >= 9:
        await update_obj.message.reply_text(
            "⚠️ شما قبلاً 9 بار لینک این فیلم را مشاهده کرده‌اید و امکان مشاهده بیشتر وجود ندارد."
        )
        return
    user_film_count[(user_id, film_code)] = count + 1
    countdown = 20
    film_msg = await update_obj.message.reply_text(
        f"✨🎥 لینک فیلم آماده است! فقط ۲۰ ثانیه فرصت داری 🖤💛\n⏳ {countdown}s",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🎥 اینجا ببین", url=link)]])
    )
    for remaining in range(countdown, 0, -1):
        try:
            await film_msg.edit_text(
                f"✨🎥 لینک فیلم آماده است! فقط ۲۰ ثانیه فرصت داری 🖤💛\n⏳ {remaining}s",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🎥 اینجا ببین", url=link)]])
            )
        except:
            pass
        await asyncio.sleep(1)
    try:
        await film_msg.edit_text(
            "🚫 لینک منقضی شد! اگر دیر کردی، دوباره روی پست کانال مراجعه کن. 🖤💛\n"
            "برای دیدن انواع فیلم و سریال به کانال اصلی و برای سکانس‌ها به اینستاگرام مراجعه کن."
        )
    except:
        pass
    asyncio.create_task(delete_message_later(update_obj.bot, film_msg.chat.id, film_msg.message_id, 200))

async def delete_message_later(bot, chat_id, message_id, delay_seconds):
    await asyncio.sleep(delay_seconds)
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
    except:
        pass

# اجرای ربات
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback))
    print("✅ Bot is running...")
    app.run_polling()
