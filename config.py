import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_BASE = os.getenv("WEBHOOK_BASE")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "webhook-123")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))
GROUP_MONITOR_ID = int(os.getenv("GROUP_MONITOR_ID", "-1001748319682"))
GROUP_PREMIUM_INVITE_LINK = os.getenv("GROUP_PREMIUM_INVITE_LINK", "")

PRICE_TEXT = "41 ₪"
BANK_DETAILS = (
    "בנק הפועלים\n"
    "סניף כפר גנים (153)\n"
    "חשבון 73462\n"
    "המוטב: קאופמן צביקה"
)
ALT_TELEGRAM_ROUTE = "UQCr743gEr_nqV_0SBkSp3CtYS_15R3LDLBvLmKeEv7XdGvp"
ASSETS_PROMO_IMAGE_PATH = "assets/promo_image.jpg"
