import os
import asyncio

from telegram import (
    Update,
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
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
    get_last_content_number,
    get_all_users,
    get_total_contents,
    get_total_views
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
        ["👥 تعداد کاربران", "📊 آمار حرفه‌ای"],
        ["📢 ارسال همگانی"],
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




if context.args:

    content_id = context.args[0]

    content = get_content(content_id)

    if content:

        content_type, file_id = content

        if content_type == "photo":

            sent_message = await update.message.reply_photo(
                file_id
            )

        elif content_type == "video":

            sent_message = await update.message.reply_video(
                file_id
            )

        else:
            return


        warning_message = await update.message.reply_text(
            "⏳ این رسانه تا ۱ دقیقه دیگر حذف می‌شود."
        )


        await asyncio.sleep(60)


        try:
            await sent_message.delete()
        except:
            pass


        try:
            await warning_message.delete()
        except:
            pass


        return


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

        keyboard = [
            [
                InlineKeyboardButton(
                    "📢 عضویت در کانال",
                    url="https://t.me/Gorgina_Fans"
                )
            ],
            [
                InlineKeyboardButton(
                    "✅ عضو شدم",
                    callback_data="check"
                )
            ]
        ]


        await update.message.reply_text(
            "برای استفاده از ربات ابتدا عضو کانال شوید.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )



async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()


    user_id = query.from_user.id


    if query.data == "check":


        if await check_member(user_id, context):

            await query.edit_message_text(
                "✅ عضویت شما تایید شد.\n\n"
                "حالا دوباره /start را بزنید."
            )

        else:

            await query.answer(
                "❌ هنوز عضو کانال نیستید.",
                show_alert=True
            )



async def messages(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id


    if user_id != ADMIN_ID:

        return



    text = update.message.text



    # ارسال همگانی

    if context.user_data.get("broadcast"):


        users = get_all_users()

        success = 0
        failed = 0


        for user in users:

            try:

                await update.message.copy(
                    chat_id=user
                )

                success += 1


            except:

                failed += 1



        context.user_data.clear()


        await update.message.reply_text(
            f"✅ ارسال انجام شد\n\n"
            f"موفق: {success}\n"
            f"ناموفق: {failed}",
            reply_markup=panel_keyboard
        )


        return




    # آپلود محتوا


    if context.user_data.get("upload"):


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
            file_id,
            upload_type
        )


        username = (
            await context.bot.get_me()
        ).username


        link = (
            f"https://t.me/{username}"
            f"?start={content_id}"
        )


        await update.message.reply_text(
            f"✅ محتوا ذخیره شد\n\n"
            f"شناسه:\n{content_id}\n\n"
            f"لینک:\n{link}"
        )


        context.user_data.clear()


        return




    if text == "👑 پنل مدیریت":


        await update.message.reply_text(
            "👑 پنل مدیریت",
            reply_markup=panel_keyboard
        )



    elif text == "👥 تعداد کاربران":


        await update.message.reply_text(
            f"👥 تعداد کاربران:\n"
            f"{get_total_users()} نفر"
        )



    elif text == "📊 آمار حرفه‌ای":


        await update.message.reply_text(
            f"📊 آمار ربات\n\n"
            f"👥 کاربران:\n"
            f"{get_total_users()}\n\n"
            f"📦 محتوا:\n"
            f"{get_total_contents()}\n\n"
            f"👁 بازدید محتوا:\n"
            f"{get_total_views()}"
        )



    elif text == "📢 ارسال همگانی":


        context.user_data["broadcast"] = True


        await update.message.reply_text(
            "📢 پیام همگانی را ارسال کن."
        )



    elif text == "📸 افزودن عکس":


        context.user_data["upload"] = "photo"


        await update.message.reply_text(
            "📸 عکس را بفرست."
        )



    elif text == "🎬 افزودن فیلم":


        context.user_data["upload"] = "video"


        await update.message.reply_text(
            "🎬 فیلم را بفرست."
        )



    elif text == "🔙 بازگشت":

        context.user_data.clear()


        await update.message.reply_text(
            "برگشتیم.",
            reply_markup=admin_keyboard
        )



async def main():

    start_server()

    init_db()


    app = Application.builder().token(TOKEN).build()



    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )



    app.add_handler(
        CallbackQueryHandler(
            button
        )
    )



    app.add_handler(
        MessageHandler(
            filters.ALL,
            messages
        )
    )



    await app.initialize()

    await app.start()

    await app.updater.start_polling()



    await asyncio.Event().wait()



if __name__ == "__main__":

    asyncio.run(main())
