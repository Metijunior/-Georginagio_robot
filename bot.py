import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

from database import init_db, add_user, get_total_users, get_today_users


TOKEN = os.getenv("BOT_TOKEN")

CHANNEL = "@Gorgina_Fans"

ADMIN_ID = 416552077


async def check_member(user_id, context):
    try:
        member = await context.bot.get_chat_member(CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    add_user(user_id)

    if await check_member(user_id, context):

        text = (
            "سلام عشق🥰\n"
            "خوش‌اومدی به ربات چنلمون❤️\n"
            "بریم که از عکس و فیلم‌ها لذت ببریم😁💦"
        )

        keyboard = []

        if user_id == ADMIN_ID:
            keyboard.append(
                [InlineKeyboardButton("👑 پنل مدیریت", callback_data="admin")]
            )

        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard) if keyboard else None
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


    if query.data == "check":

        if await check_member(user_id, context):

            add_user(user_id)

            text = (
                "سلام عشق🥰\n"
                "خوش‌اومدی به ربات چنلمون❤️\n"
                "بریم که از عکس و فیلم‌ها لذت ببریم😁💦"
            )

            keyboard = []

            if user_id == ADMIN_ID:
                keyboard.append(
                    [InlineKeyboardButton("👑 پنل مدیریت", callback_data="admin")]
                )

            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup(keyboard) if keyboard else None
            )

        else:
            await query.answer(
                "❌ هنوز عضو کانال نشدی",
                show_alert=True
            )


    elif query.data == "admin":

        if user_id != ADMIN_ID:
            return

        keyboard = [
            [InlineKeyboardButton("👥 تعداد کاربران", callback_data="users")],
            [InlineKeyboardButton("📈 آمار امروز", callback_data="today")]
        ]

        await query.edit_message_text(
            "👑 پنل مدیریت",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


    elif query.data == "users":

        if user_id == ADMIN_ID:

            await query.edit_message_text(
                f"👥 تعداد کل کاربران:\n\n{get_total_users()} نفر"
            )


    elif query.data == "today":

        if user_id == ADMIN_ID:

            await query.edit_message_text(
                f"📈 کاربران امروز:\n\n{get_today_users()} نفر"
            )


async def main():

    init_db()

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))


    await app.initialize()
    await app.start()
    await app.updater.start_polling()


    await asyncio.Event().wait()



if __name__ == "__main__":
    asyncio.run(main())
