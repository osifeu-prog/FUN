import logging
from typing import Dict

from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Update,
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    InputFile,
)
from aiogram.filters import CommandStart
from aiogram.enums import ChatType

from config import (
    BOT_TOKEN,
    WEBHOOK_BASE,
    WEBHOOK_SECRET,
    ADMIN_CHAT_ID,
    GROUP_MONITOR_ID,
    GROUP_PREMIUM_INVITE_LINK,
    PRICE_TEXT,
    BANK_DETAILS,
    ALT_TELEGRAM_ROUTE,
    ASSETS_PROMO_IMAGE_PATH,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

fastapi_app = FastAPI()

# מצב משתמשים בזיכרון
user_states: Dict[int, Dict] = {}

# Keyboards
def main_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="מה הבוט הזה יכול לעשות?", callback_data="learn_1")]
        ]
    )

def after_share_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="בדקתי, מה הלאה?", callback_data="learn_2")]
        ]
    )

def admin_approval_keyboard(user_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="אשר", callback_data=f"admin_approve:{user_id}"),
                InlineKeyboardButton(text="דחה", callback_data=f"admin_reject:{user_id}"),
            ]
        ]
    )

# Handlers
@dp.message(CommandStart())
async def on_start(message: Message):
    user_id = message.from_user.id
    user_states.setdefault(user_id, {"shared_ok": False, "payment_proof_msg_id": None, "approved": False})

    text = (
        "ברוך/ה הבא/ה! לחיצה על הכפתור תסביר מה הבוט הזה יכול לעשות.\n"
        "בכל פעם שמשתמש נכנס לבוט, תישלח לי התראה.\n"
        "מוכן/ה להתחיל?"
    )
    await message.answer(text, reply_markup=main_keyboard())

    if ADMIN_CHAT_ID:
        await bot.send_message(
            ADMIN_CHAT_ID,
            f"משתמש חדש התחיל את הבוט: @{message.from_user.username or 'ללא'} (ID: {user_id})"
        )

@dp.callback_query(F.data == "learn_1")
async def learn_first_step(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_states.setdefault(user_id, {"shared_ok": False, "payment_proof_msg_id": None, "approved": False})

    text = (
        "בוט ההזדמנויות: רוצה ללמוד מה הוא עושה?\n\n"
        "ראשית, שלח את הבוט לחבר טוב שמבין צחוקים (לא לאמא או אבא 😉).\n"
        "גישה תינתן רק לאחר אימות שנשלחה ההודעה למשתמש אחר.\n\n"
        "לאחר שסיימת, לחץ שוב כדי להמשיך."
    )
    await callback.message.edit_text(text, reply_markup=after_share_keyboard())
    await callback.answer()

@dp.callback_query(F.data == "learn_2")
async def learn_second_step(callback: CallbackQuery):
    user_id = callback.from_user.id
    state = user_states.setdefault(user_id, {"shared_ok": False, "payment_proof_msg_id": None, "approved": False})

    if not state["shared_ok"]:
        state["shared_ok"] = True
        await callback.message.edit_text(
            "מצוין! עכשיו שלב התשלום כדי לפתוח את כל ההטבות.\n\n"
            f"אנא שלח כאן צילום מסך/תמונה של אישור הפקדה על סך {PRICE_TEXT}.\n"
            "פרטי הפקדה:\n"
            f"{BANK_DETAILS}\n\n"
            "או דרך הטלגרם:\n"
            f"{ALT_TELEGRAM_ROUTE}\n\n"
            "לאחר שתעלה את התמונה, אשלח לך אישור/דחייה בהתאם."
        )
    else:
        await callback.message.edit_text(
            "כדי לראות עוד שימושים, עליך להשלים שלב האישור. "
            "אנא העלה תמונת אישור הפקדה כאן."
        )
    await callback.answer()

@dp.message(F.photo)
async def on_payment_proof(message: Message):
    user_id = message.from_user.id
    state = user_states.setdefault(user_id, {"shared_ok": False, "payment_proof_msg_id": None, "approved": False})
    state["payment_proof_msg_id"] = message.message_id

    await message.reply("קיבלתי את אישור התשלום. שולח לאדמין לבדיקה...")

    if ADMIN_CHAT_ID:
        caption = (
            f"אישור תשלום חדש לבדיקה:\n"
            f"משתמש: @{message.from_user.username or 'ללא'} (ID: {user_id})\n"
            f"סכום: {PRICE_TEXT}\n"
            "לאשר או לדחות?"
        )
        photo = message.photo[-1]
        file_id = photo.file_id

        await bot.send_photo(
            chat_id=ADMIN_CHAT_ID,
            photo=file_id,
            caption=caption,
            reply_markup=admin_approval_keyboard(user_id),
        )

    try:
        await bot.send_photo(
            chat_id=user_id,
            photo=InputFile(ASSETS_PROMO_IMAGE_PATH),
            caption="הנה התמונה מהפרויקט בגיט."
        )
    except Exception as e:
        logger.warning(f"שליחת תמונת פרומו נכשלה: {e}")

@dp.callback_query(F.data.startswith("admin_approve:"))
async def admin_approve(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_CHAT_ID:
        await callback.answer("רק אדמין יכול לבצע פעולה זו.", show_alert=True)
        return

    _, user_id_str = callback.data.split(":")
    target_user_id = int(user_id_str)
    state = user_states.setdefault(target_user_id, {"shared_ok": False, "payment_proof_msg_id": None, "approved": False})
    state["approved"] = True

    await callback.message.edit_caption((callback.message.caption or "") + "\n\nסטטוס: אושר ✅")
    await callback.answer("אושר")

    try:
        await bot.send_message(
            chat_id=target_user_id,
            text=(
                "אושר! הנה ההזמנה לקבוצה הפרימיום:\n"
                f"{GROUP_PREMIUM_INVITE_LINK}\n\n"
                "בקהילה הזו תנתן גישה להמון בוטים והטבות!"
            )
        )
    except Exception as e:
        logger.error(f"שליחת הזמנה נכשלה ל-{target_user_id}: {e}")

@dp.callback_query(F.data.startswith("admin_reject:"))
async def admin_reject(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_CHAT_ID:
        await callback.answer("רק אדמין יכול לבצע פעולה זו.", show_alert=True)
        return

    _, user_id_str = callback.data.split(":")
    target_user_id = int(user_id_str)
    state = user_states.setdefault(target_user_id, {"shared_ok": False, "payment_proof_msg_id": None, "approved": False})
    state["approved"] = False

    await callback.message.edit_caption((callback.message.caption or "") + "\n\nסטטוס: נדחה ❌")
    await callback.answer("נדחה")

    try:
        await bot.send_message(
            chat_id=target_user_id,
            text="הבקשה נדחתה. אנא ודא שהעלית אישור תקין."
        )
    except Exception as e:
        logger.error(f"שליחת הודעת דחייה נכשלה ל-{target_user_id}: {e}")

@dp.message()
async def on_any_message(message: Message):
    if message.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP):
        if message.chat.id == GROUP_MONITOR_ID and message.new_chat_members:
            for m in message.new_chat_members:
                if ADMIN_CHAT_ID:
                    await bot.send_message(
                        ADMIN_CHAT_ID,
                        f"משתמש נכנס לקבוצה: @{m.username or 'ללא'} (ID: {m.id})"
                    )
    elif message.chat.type == ChatType.PRIVATE and not message.photo:
        await message.answer(
            "לחץ על הכפתור כדי ללמוד מה הבוט הזה יכול לעשות.",
            reply_markup=main_keyboard()
        )

# --- Webhook setup ---
@fastapi_app.on_event("startup")
async def on_startup():
    webhook_url = f"{WEBHOOK_BASE}/{WEBHOOK_SECRET}"
    try:
        await bot.set_webhook(url=webhook_url)
        logger.info(f"Webhook set to: {webhook_url}")
    except Exception as e:
        logger.error(f"Failed to set webhook: {e}")

@fastapi_app.post("/{secret_path}")
async def handle_update(secret_path
