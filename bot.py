import os
import asyncio

from telegram import (
    Update,
    KeyboardButton,
    ReplyKeyboardMarkup
)

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from database import (
    init_db,
    add_user,
    get_total_users,
    get_today_users,
    add_content,
    get_content,
    get_last_content_number
)

from server import start_server


TOKEN = os.getenv("BOT_TOKEN")

CHANNEL = "@Gorgina_Fans"

ADMIN_ID = 416552077


admin_keyboard = ReplyKeyboardMarkup(
    [
        [KeyboardButton("👑 پنل مدیریت")]
    ],
    resize_keyboard=True
)


panel_keyboard = ReplyKeyboardMarkup(
    [
        ["👥 تعداد کاربران", "📈 آمار امروز"],
        ["📸 افزودن عکس", "🎬 افزودن فیلم"],
        ["🔙 بازگشت"]
    ],
    resize_keyboard=True
)


async def check_member(user_id, context):

    try:
        member = await context.bot.get_chat_member(
            CHANNEL,
            user_id
        )

        return member.status in [
            "member",
            "administrator",
            "creator"
        ]

    except:
        return False



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    add_user(user_id)


    # لینک اختصاصی محتوا
    if context.args:

        content_id = context.args[0]

        content = get_content(content_id)

        if content:

            content_type, file_id = content

            if content_type == "photo":

                await update.message.reply_photo(
                    file_id
                )

            elif content_type == "video":

                await update.message.reply_video(
                    file_id
                )

            return



    if await check_member(user_id, context):

        text = (
            "سلام عشق🥰\n"
            "خوش‌اومدی به ربات چنلمون❤️\n"
            "بریم که از عکس و فیلم‌ها لذت ببریم😁💦"
        )


        if user_id == ADMIN_ID:

            await update.message.reply_text(
                text,
                reply_markup=admin_keyboard
            )

        else:

            await update.message.reply_text(
                text
            )


    else:

        await update.message.reply_text(
            "برای استفاده از ربات ابتدا عضو کانال شوید."
        )



async def messages(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    text = update.message.text


    if user_id != ADMIN_ID:
        return



    if text == "👑 پنل مدیریت":

        await update.message.reply_text(
            "👑 پنل مدیریت",
            reply_markup=panel_keyboard
        )


    elif text == "👥 تعداد کاربران":

        await update.message.reply_text(
            f"👥 تعداد کل کاربران:\n\n{get_total_users()} نفر"
        )


    elif text == "📈 آمار امروز":

        await update.message.reply_text(
            f"📈 کاربران امروز:\n\n{get_today_users()} نفر"
        )


    elif text == "📸 افزودن عکس":

        context.user_data["upload"] = "photo"

        await update.message.reply_text(
            "📸 عکس را ارسال کن."
        )


    elif text == "🎬 افزودن فیلم":

        context.user_data["upload"] = "video"

        await update.message.reply_text(
            "🎬 فیلم را ارسال کن."
        )


    elif text == "🔙 بازگشت":

        await update.message.reply_text(
            "برگشتیم.",
            reply_markup=admin_keyboard
        )



    elif "upload" in context.user_data:


        upload_type = context.user_data["upload"]


        if upload_type == "photo" and update.message.photo:

            file_id = update.message.photo[-1].file_id


        elif upload_type == "video" and update.message.video:

            file_id = update.message.video.file_id


        else:

            return


        number = get_last_content_number()


        content_id = f"{upload_type}_{number}"


        add_content(
            content_id,
            upload_type,
            file_id
        )


        bot_username = (await context.bot.get_me()).username


        link = (
            f"https://t.me/{bot_username}"
            f"?start={content_id}"
        )


        await update.message.reply_text(
            f"✅ ذخیره شد\n\n"
            f"شناسه:\n{content_id}\n\n"
            f"لینک اختصاصی:\n{link}"
        )


        context.user_data.clear()



async def main():

    start_server()

    init_db()


    app = Application.builder().token(TOKEN).build()


    app.add_handler(
        CommandHandler("start", start)
    )


    app.add_handler(
        MessageHandler(
            filters.TEXT | filters.PHOTO | filters.VIDEO,
            messages
        )
    )


    await app.initialize()
    await app.start()
    await app.updater.start_polling()


    await asyncio.Event().wait()



if __name__ == "__main__":

    asyncio.run(main())
