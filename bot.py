import bale
import asyncio
import os

TOKEN = os.environ["BOT_TOKEN"]
ADMIN_CHAT_ID = os.environ.get("ADMIN_CHAT_ID", "")  # optional: your Bale user ID for enrollment notifications

COURSES = {
    "a1": {"title": "انگلیسی مبتدی",   "cefr": "A1 — Starter",            "price": 14500000, "label": "۱،۴۵۰،۰۰۰ تومان"},
    "a2": {"title": "انگلیسی پایه",     "cefr": "A2 — Elementary",         "price": 16500000, "label": "۱،۶۵۰،۰۰۰ تومان"},
    "b1": {"title": "انگلیسی متوسط",    "cefr": "B1 — Intermediate",       "price": 20000000, "label": "۲،۰۰۰،۰۰۰ تومان"},
    "b2": {"title": "انگلیسی متوسط بالا","cefr": "B2 — Upper-Intermediate", "price": 25000000, "label": "۲،۵۰۰،۰۰۰ تومان"},
    "c1": {"title": "انگلیسی پیشرفته",  "cefr": "C1 — Advanced",           "price": 32000000, "label": "۳،۲۰۰،۰۰۰ تومان"},
    "kids":{"title": "انگلیسی کودکان", "cefr": "Friends First",            "price": 17500000, "label": "۱،۷۵۰،۰۰۰ تومان"},
}

# Prices are in Rials (Bale invoices use Rial). Values above × 10 already.
# e.g. 1,450,000 Toman = 14,500,000 Rial

client = bale.Bot(token=TOKEN)


@client.event
async def on_ready():
    await client.delete_webhook()
    print(f"Bot ready: {client.user}")


@client.event
async def on_message(message: bale.Message):
    if not message.text:
        return

    text = message.text.strip()

    # /start with optional course param: /start b1
    if text.startswith("/start"):
        parts = text.split()
        course_id = parts[1].lower() if len(parts) > 1 else None

        if course_id and course_id in COURSES:
            await send_course_invoice(message, course_id)
        else:
            await send_main_menu(message)

    elif text == "📚 دوره‌ها":
        await send_course_list(message)

    elif text in COURSES:
        await send_course_invoice(message, text)

    elif text == "📞 پشتیبانی":
        await message.reply(
            "برای ارتباط با پشتیبانی لینگویا:\n"
            "📱 تلگرام: @linguyacademy\n"
            "📧 ایمیل: info@linguyacademy.ir\n"
            "📍 آدرس: خلخال، استان اردبیل"
        )

    elif text == "🌐 وب‌سایت":
        await message.reply("وب‌سایت آکادمی لینگویا:\nhttp://linguyacademy.ir/")


@client.event
async def on_successful_payment(payment: bale.SuccessfulPayment, message: bale.Message):
    course_id = payment.invoice_payload
    course = COURSES.get(course_id, {})

    confirm_text = (
        f"✅ پرداخت موفق!\n\n"
        f"🎓 دوره: {course.get('title', '—')}\n"
        f"💰 مبلغ: {course.get('label', '—')}\n"
        f"🆔 کد پیگیری: LQ-{message.from_user.id}-{payment.telegram_payment_charge_id[:8]}\n\n"
        f"تیم لینگویا ظرف ۲۴ ساعت با شما تماس می‌گیرد و جزئیات کلاس را ارسال می‌کند.\n"
        f"موفق باشید! 🌟"
    )
    await message.reply(confirm_text)

    # Notify admin
    if ADMIN_CHAT_ID and ADMIN_CHAT_ID != "YOUR_ADMIN_CHAT_ID":
        admin_text = (
            f"🔔 ثبت‌نام جدید!\n"
            f"👤 کاربر: {message.from_user.first_name} {message.from_user.last_name or ''}\n"
            f"🆔 ID: {message.from_user.id}\n"
            f"📚 دوره: {course.get('title', course_id)}\n"
            f"💰 مبلغ: {course.get('label', '—')}\n"
            f"🧾 کد: {payment.telegram_payment_charge_id}"
        )
        try:
            await client.send_message(ADMIN_CHAT_ID, admin_text)
        except Exception:
            pass


async def send_main_menu(message: bale.Message):
    keyboard = bale.ReplyKeyboardMarkup()
    keyboard.add(bale.KeyboardButton("📚 دوره‌ها"))
    keyboard.add(bale.KeyboardButton("📞 پشتیبانی"))
    keyboard.add(bale.KeyboardButton("🌐 وب‌سایت"))

    await message.reply(
        "سلام! 👋 به ربات آکادمی زبان لینگویا خوش آمدید.\n\n"
        "از منو زیر انتخاب کنید:",
        components=keyboard
    )


async def send_course_list(message: bale.Message):
    keyboard = bale.ReplyKeyboardMarkup()
    for cid, c in COURSES.items():
        keyboard.add(bale.KeyboardButton(cid))

    lines = ["📚 دوره‌های موجود:\n"]
    for cid, c in COURSES.items():
        lines.append(f"• *{c['title']}* ({c['cefr']}) — {c['label']}")
    lines.append("\nبرای ثبت‌نام، کد دوره را ارسال کنید (مثال: b1)")

    await message.reply("\n".join(lines), components=keyboard)


async def send_course_invoice(message: bale.Message, course_id: str):
    course = COURSES[course_id]

    await client.send_invoice(
        chat_id=message.chat.id,
        title=f"دوره {course['title']}",
        description=(
            f"{course['cefr']}\n"
            f"۱۲ جلسه ۷۵ دقیقه‌ای · گواهی پایان دوره · پشتیبانی استاد\n"
            f"آکادمی زبان لینگویا — خلخال، اردبیل"
        ),
        payload=course_id,
        provider_token="",  # Bale's built-in payment — leave empty for Bale Wallet
        prices=[bale.LabeledPrice(label=course['title'], amount=course['price'])],
        photo_url="http://linguyacademy.ir/og-image.jpg",  # optional cover image
        need_name=True,
        need_phone_number=True,
        need_email=False,
        is_flexible=False,
    )


if __name__ == "__main__":
    client.run()
