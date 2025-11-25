import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")  # טוקן הבוט מה-BotFather
WEBHOOK_BASE = os.getenv("WEBHOOK_BASE")  # למשל https://your.domain.com
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "super-secret-path")  # path ייחודי
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))  # ה-Chat ID שלך לאישורים
GROUP_MONITOR_ID = int(os.getenv("GROUP_MONITOR_ID", "-1001748319682"))  # הקבוצה למעקב כניסות
GROUP_PREMIUM_INVITE_LINK = os.getenv("GROUP_PREMIUM_INVITE_LINK", "https://t.me/+HIzvM8sEgh1kNWY0")  # הזמנה אחרי תשלום

# טקסטים ושדות קבועים
PRICE_TEXT = "41 ₪"
BANK_DETAILS = (
    "בנק הפועלים\n"
    "סניף כפר גנים (153)\n"
    "חשבון 73462\n"
    "המוטב: קאופמן צביקה"
)
ALT_TELEGRAM_ROUTE = "UQCr743gEr_nqV_0SBkSp3CtYS_15R3LDLBvLmKeEv7XdGvp"  # לפי הבקשה
ASSETS_PROMO_IMAGE_PATH = "assets/promo_image.jpg"
