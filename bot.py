import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")

CHANNEL = "@Gorgina_Fans"


async def check_member(user_id, context):
    try:
        member = await context.bot.get_chat_member(CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if await check_member(user_id, context):
        await update.message.reply_text(
    "سلام عشق🥰\n"
    "خوش‌اومدی به ربات چنلمون❤️\n"
    "بریم که از عکس و فیلم‌ها لذت ببریم😁💦"
        )
        )
    else:
        keyboard = [
            [InlineKeyboardButton("📢 عضویت در کانال", url="https://t.me/Gorgina_Fans")],
            [InlineKeyboardButton("✅ عضو شدم", callback_data="check")]
        ]

        await update.message.reply_text(
            "برای استفاده از ربات ابتدا عضو کانال شوید:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if await check_member(user_id, context):
        await query.edit_message_text("✅ عضویت تایید شد.\nخوش آمدید!")
    else:
        await query.answer("❌ هنوز عضو کانال نشده‌اید.", show_alert=True)


async def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))

    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
