import bale
import asyncio
import os

TOKEN = os.environ["BOT_TOKEN"]
ADMIN_CHAT_ID = os.environ.get("ADMIN_CHAT_ID", "")  # optional: your Bale user ID for enrollment notifications
# How you receive money on Bale: your card number (16 digits) OR Bale wallet number.
# Set as Railway variable PROVIDER_TOKEN. Without it, invoices show but no real payout.
PROVIDER_TOKEN = os.environ.get("PROVIDER_TOKEN", "")

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

    # /start with optional course param: /start b1  (case-insensitive: Bale sends "/Start")
    if text.lower().startswith("/start"):
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
async def on_successful_payment(payment: bale.SuccessfulPayment):
    course_id = payment.invoice_payload
    course = COURSES.get(course_id, {})

    # Notify admin (Bale's SuccessfulPayment has no buyer info, so we rely on admin notice).
    if ADMIN_CHAT_ID:
        admin_text = (
            f"🔔 ثبت‌نام و پرداخت جدید!\n"
            f"📚 دوره: {course.get('title', course_id)}\n"
            f"💰 مبلغ پرداختی: {payment.total_amount:,} {payment.currency}\n"
            f"🧾 payload: {course_id}"
        )
        try:
            await client.send_message(ADMIN_CHAT_ID, admin_text)
        except Exception:
            pass


async def send_main_menu(message: bale.Message):
    keyboard = bale.MenuKeyboardMarkup()
    keyboard.add(bale.MenuKeyboardButton("📚 دوره‌ها"))
    keyboard.add(bale.MenuKeyboardButton("📞 پشتیبانی"))
    keyboard.add(bale.MenuKeyboardButton("🌐 وب‌سایت"))

    await message.reply(
        "سلام! 👋 به ربات آکادمی زبان لینگویا خوش آمدید.\n\n"
        "از منو زیر انتخاب کنید:",
        components=keyboard
    )


async def send_course_list(message: bale.Message):
    keyboard = bale.MenuKeyboardMarkup()
    for cid, c in COURSES.items():
        keyboard.add(bale.MenuKeyboardButton(cid))

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
        provider_token=PROVIDER_TOKEN,  # your card/wallet number, set via Railway PROVIDER_TOKEN var
        prices=[bale.LabeledPrice(label=course['title'], amount=course['price'])],
        photo_url="http://linguyacademy.ir/og-image.jpg",  # optional cover image
        need_name=True,
        need_phone_number=True,
        need_email=False,
        is_flexible=False,
    )


if __name__ == "__main__":
    client.run()
