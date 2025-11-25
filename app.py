import logging
from typing import Dict

from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, F
from aiogram.types import Update, Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputFile
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

# --- Endpoints לבדיקה בדפדפן ---
@fastapi_app.get("/")
async def root():
    return {"status": "up", "service": "FUN bot"}

@fastapi_app.get("/health")
async def health():
    return {"status": "ok"}

@fastapi_app.get("/debug")
async def debug():
    return {
        "webhook_base": WEBHOOK_BASE,
        "webhook_secret": WEBHOOK_SECRET,
        "has_token": bool(BOT_TOKEN),
    }

# --- לוגיקת הבוט שלך (כמו קודם) ---
user_states: Dict[int, Dict] = {}

def main_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="מה הבוט הזה יכול לעשות?", callback_data="learn_1")]]
    )

def after_share_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="בדקתי, מה הלאה?", callback_data="learn_2")]]
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

@dp.message(CommandStart())
async def on_start(message: Message):
    user_id = message.from_user.id
    user_states.setdefault(user_id, {"shared_ok": False, "payment_proof_msg_id": None, "approved": False})
    await message.answer("ברוך/ה הבא/ה! לחץ על הכפתור כדי להתחיל.", reply_markup=main_keyboard())
    if ADMIN_CHAT_ID:
        await bot.send_message(ADMIN_CHAT_ID, f"משתמש חדש: @{message.from_user.username or 'ללא'} (ID: {user_id})")

# ... (שאר ההנדלרים שלך בדיוק כמו קודם) ...

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
async def handle_update(secret_path: str, request: Request):
    if secret_path != WEBHOOK_SECRET:
        return {"status": "ignored"}
    body = await request.json()
    update = Update.model_validate(body)
    await dp.feed_update(bot, update)
    return {"status": "ok"}

@fastapi_app.on_event("shutdown")
async def on_shutdown():
    try:
        await bot.delete_webhook()
    except Exception as e:
        logger.error(f"Failed to delete webhook: {e}")
    await bot.session.close()
