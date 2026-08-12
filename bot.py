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
    get_total_views,
    create_collection,
    add_to_collection,
    get_collection
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
        ["📦 ساخت مجموعه"],
        ["🔙 بازگشت"]
    ],
    resize_keyboard=True
)


collection_keyboard = ReplyKeyboardMarkup(
    [
        ["✅ پایان مجموعه"],
        ["❌ لغو مجموعه"]
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

    except Exception:

        return False


async def delete_media_later(
    bot,
    chat_id,
    message_ids
):

    await asyncio.sleep(60)

    for message_id in message_ids:

        try:

            await bot.delete_message(
                chat_id=chat_id,
                message_id=message_id
            )

        except Exception:

            pass


async def send_content(
    update,
    context,
    content_id
):

    content = get_content(content_id)

    if not content:
        return False


    content_type, file_id, caption = content


    if content_type == "photo":

        sent = await update.message.reply_photo(
            photo=file_id,
            caption=caption or None
        )


    elif content_type == "video":

        sent = await update.message.reply_video(
            video=file_id,
            caption=caption or None
        )


    else:

        return False


    warning = await update.message.reply_text(
        "⏳ این رسانه تا ۱ دقیقه دیگر حذف می‌شود."
    )


    asyncio.create_task(
        delete_media_later(
            context.bot,
            update.effective_chat.id,
            [
                sent.message_id,
                warning.message_id
            ]
        )
    )


    return True


async def send_collection(
    update,
    context,
    content_ids
):

    message_ids = []


    for content_id in content_ids:

        content = get_content(content_id)

        if not content:
            continue


        content_type, file_id, caption = content


        if content_type == "photo":

            sent = await update.message.reply_photo(
                photo=file_id,
                caption=caption or None
            )


        elif content_type == "video":

            sent = await update.message.reply_video(
                video=file_id,
                caption=caption or None
            )


        else:

            continue


        message_ids.append(
            sent.message_id
        )


    if not message_ids:
        return


    warning = await update.message.reply_text(
        "⏳ این مجموعه تا ۱ دقیقه دیگر حذف می‌شود."
    )


    message_ids.append(
        warning.message_id
    )


    asyncio.create_task(
        delete_media_later(
            context.bot,
            update.effective_chat.id,
            message_ids
        )
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    add_user(user_id)


    if context.args:

        content_id = context.args[0]


        # لینک مجموعه
        if content_id.startswith("collection_"):

            collection = get_collection(content_id)

            if collection:

                await send_collection(
                    update,
                    context,
                    collection
                )

                return


        # لینک تک رسانه
        if await send_content(
            update,
            context,
            content_id
        ):

            return


    if await check_member(
        user_id,
        context
    ):

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
            reply_markup=InlineKeyboardMarkup(
                keyboard
            )
        )


async def button(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    user_id = query.from_user.id


    if query.data == "check":

        if await check_member(
            user_id,
            context
        ):

            add_user(user_id)

            await query.edit_message_text(
                "✅ عضویت شما تایید شد.\n\n"
                "حالا دوباره /start را بزنید."
            )

        else:

            await query.answer(
                "❌ هنوز عضو کانال نیستید.",
                show_alert=True
            )


async def messages(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id

    if user_id != ADMIN_ID:
        return


    message = update.message

    text = message.text or ""


    # =========================
    # 📢 ارسال همگانی
    # =========================

    if context.user_data.get("broadcast"):

        users = get_all_users()

        success = 0
        failed = 0


        for user in users:

            try:

                await message.copy(
                    chat_id=user
                )

                success += 1

            except Exception:

                failed += 1


        context.user_data.clear()


        await message.reply_text(
            f"✅ ارسال همگانی انجام شد\n\n"
            f"موفق: {success}\n"
            f"ناموفق: {failed}",
            reply_markup=panel_keyboard
        )

        return


    # =========================
    # 📦 آپلود مجموعه
    # =========================

    if context.user_data.get("collection"):

        # پایان مجموعه

        if text == "✅ پایان مجموعه":

            items = context.user_data.get(
                "collection_items",
                []
            )


            if not items:

                await message.reply_text(
                    "❌ هنوز هیچ رسانه‌ای اضافه نکردی."
                )

                return


            number = get_last_content_number()

            collection_id = (
                f"collection_{number}"
            )


            create_collection(collection_id)

            for position, item_id in enumerate(items, start=1):

                add_to_collection(
                    collection_id,
                    item_id,
                    position
                )


            bot_info = await context.bot.get_me()

            bot_username = bot_info.username


            link = (
                f"https://t.me/"
                f"{bot_username}"
                f"?start={collection_id}"
            )


            await message.reply_text(
                f"✅ مجموعه ساخته شد!\n\n"
                f"🎬 تعداد رسانه‌ها: "
                f"{len(items)}\n\n"
                f"🔗 لینک اختصاصی:\n"
                f"{link}",
                reply_markup=panel_keyboard
            )


            context.user_data.clear()

            return


        # لغو مجموعه

        if text == "❌ لغو مجموعه":

            context.user_data.clear()

            await message.reply_text(
                "❌ ساخت مجموعه لغو شد.",
                reply_markup=panel_keyboard
            )

            return


        # دریافت عکس

        if message.photo:

            file_id = message.photo[-1].file_id

            caption = message.caption or ""


            number = get_last_content_number()

            content_id = f"photo_{number}"


            add_content(
                content_id,
                "photo",
                file_id,
                "photo",
                caption
            )


            items = context.user_data.setdefault(
                "collection_items",
                []
            )


            items.append(
                content_id
            )


            await message.reply_text(
                f"✅ عکس {len(items)} به مجموعه اضافه شد.\n\n"
                f"برای اضافه کردن رسانه بعدی، "
                f"همان‌طور ارسالش کن.\n\n"
                f"وقتی تمام شد:\n"
                f"«✅ پایان مجموعه»"
            )

            return


        # دریافت فیلم

        if message.video:

            file_id = message.video.file_id

            caption = message.caption or ""


            number = get_last_content_number()

            content_id = f"video_{number}"


            add_content(
                content_id,
                "video",
                file_id,
                "video",
                caption
            )


            items = context.user_data.setdefault(
                "collection_items",
                []
            )


            items.append(
                content_id
            )


            await message.reply_text(
                f"✅ فیلم {len(items)} به مجموعه اضافه شد.\n\n"
                f"برای اضافه کردن رسانه بعدی، "
                f"همان‌طور ارسالش کن.\n\n"
                f"وقتی تمام شد:\n"
                f"«✅ پایان مجموعه»"
            )

            return


    # =========================
    # 📸 آپلود تک رسانه
    # =========================

    if context.user_data.get("upload"):

        upload_type = context.user_data[
            "upload"
        ]


        # عکس

        if (
            upload_type == "photo"
            and message.photo
        ):

            file_id = message.photo[-1].file_id

            caption = message.caption or ""


        # فیلم

        elif (
            upload_type == "video"
            and message.video
        ):

            file_id = message.video.file_id

            caption = message.caption or ""


        else:

            await message.reply_text(
                "❌ فایل مناسب ارسال نشده."
            )

            return


        number = get_last_content_number()

        content_id = (
            f"{upload_type}_{number}"
        )


        add_content(
            content_id,
            upload_type,
            file_id,
            upload_type,
            caption
        )


        bot_info = await context.bot.get_me()

        bot_username = bot_info.username


        link = (
            f"https://t.me/"
            f"{bot_username}"
            f"?start={content_id}"
        )


        await message.reply_text(
            f"✅ محتوا ذخیره شد.\n\n"
            f"🆔 شناسه:\n"
            f"{content_id}\n\n"
            f"🔗 لینک اختصاصی:\n"
            f"{link}",
            reply_markup=panel_keyboard
        )


        context.user_data.clear()

        return


    # =========================
    # 👑 پنل مدیریت
    # =========================

    if text == "👑 پنل مدیریت":

        await message.reply_text(
            "👑 پنل مدیریت",
            reply_markup=panel_keyboard
        )

        return


    # =========================
    # 👥 تعداد کاربران
    # =========================

    if text == "👥 تعداد کاربران":

        await message.reply_text(
            f"👥 تعداد کاربران:\n\n"
            f"{get_total_users()} نفر"
        )

        return


    # =========================
    # 📊 آمار حرفه‌ای
    # =========================

    if text == "📊 آمار حرفه‌ای":

        await message.reply_text(
            f"📊 آمار ربات\n\n"
            f"👥 کل کاربران:\n"
            f"{get_total_users()}\n\n"
            f"📈 کاربران امروز:\n"
            f"{get_today_users()}\n\n"
            f"📦 تعداد محتوا:\n"
            f"{get_total_contents()}\n\n"
            f"👁 مجموع بازدید:\n"
            f"{get_total_views()}"
        )

        return


    # =========================
    # 📢 ارسال همگانی
    # =========================

    if text == "📢 ارسال همگانی":

        context.user_data[
            "broadcast"
        ] = True


        await message.reply_text(
            "📢 پیام همگانی را ارسال کن.\n\n"
            "متن، عکس یا فیلم می‌توانی بفرستی.\n\n"
            "برای لغو، «🔙 بازگشت» را بزن."
        )

        return


    # =========================
    # 📸 افزودن عکس
    # =========================

    if text == "📸 افزودن عکس":

        context.user_data[
            "upload"
        ] = "photo"


        await message.reply_text(
            "📸 عکس را همراه با کپشن دلخواهت ارسال کن."
        )

        return


    # =========================
    # 🎬 افزودن فیلم
    # =========================

    if text == "🎬 افزودن فیلم":

        context.user_data[
            "upload"
        ] = "video"


        await message.reply_text(
            "🎬 فیلم را همراه با کپشن دلخواهت ارسال کن."
        )

        return


    # =========================
    # 📦 ساخت مجموعه
    # =========================

    if text == "📦 ساخت مجموعه":

        context.user_data.clear()

        context.user_data[
            "collection"
        ] = True

        context.user_data[
            "collection_items"
        ] = []


        await message.reply_text(
            "📦 حالت ساخت مجموعه فعال شد.\n\n"
            "حالا عکس‌ها و فیلم‌ها را یکی‌یکی "
            "برای من ارسال کن.\n\n"
            "برای هر رسانه می‌توانی کپشن جداگانه "
            "بگذاری.\n\n"
            "وقتی تمام شد، دکمه:\n"
            "«✅ پایان مجموعه»\n"
            "را بزن.",
            reply_markup=collection_keyboard
        )

        return


    # =========================
    # 🔙 بازگشت
    # =========================

    if text == "🔙 بازگشت":

        context.user_data.clear()

        await message.reply_text(
            "برگشتیم.",
            reply_markup=admin_keyboard
        )

        return


# ==========================================
# MAIN
# ==========================================

async def main():

    start_server()

    init_db()


    if not TOKEN:

        raise RuntimeError(
            "BOT_TOKEN environment variable is not set."
        )


    app = (
        Application.builder()
        .token(TOKEN)
        .build()
    )


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

