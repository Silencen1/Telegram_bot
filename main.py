import logging
import asyncio
import json
import os


from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")

# Log sozlamalari
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Fayldan o'qish/yozish funksiyalari
VERIFIED_FILE = 'verified_users.json'

def load_verified():
    try:
        with open(VERIFIED_FILE, 'r') as f:
            return set(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()

def save_verified(user_ids):
    with open(VERIFIED_FILE, 'w') as f:
        json.dump(list(user_ids), f)

# Kerakli kanallar
REQUIRED_CHANNELS = ['@ujas_kino18', '@xtzhsrfdskhso']

# Menyu variantlari
MENU_BUTTONS = [
    ['Logolar', 'Manchestr City'],
    ['Al-Nasr', 'Real Madrid'],
    ['Manchestr United', 'Yordam']
]

# Har bir menyu uchun URL/rasm ro'yxatlari
MEDIA_MAP = {
    'Logolar': [
        'https://kitdls.net/wp-content/uploads/2023/12/DLS-512x512-Logo-Manchester-City.png',
        'https://kitdls.net/wp-content/uploads/2024/01/dls-512x512-logo-al-nassr.png',
        'https://kitdls.net/wp-content/uploads/2023/09/Logo-Barcelona-Dream-League-Soccer-1.png',
        'https://kitdls.net/wp-content/uploads/2023/09/Logo-Barcelona-Dream-League-Soccer-2.png',
        'https://kitdls.net/wp-content/uploads/2023/09/Logo-Manchester-Utd-2023-2024-DLS-1.png',
        'https://kitdls.net/wp-content/uploads/2023/09/Logo-Manchester-Utd-2023-2024-DLS.png'
    ],
    'Manchestr City': [
        'https://dlsgame.net/wp-content/uploads/2025/03/MC-Home-Kit-25-DLS-25.png',
        'https://dlsgame.net/wp-content/uploads/2025/03/MC-Away-Kit-25-DLS-25.png',
        'https://kitdls.net/wp-content/uploads/2024/08/Manchester-City-Home-Kit-V2-2024-2025-DLS-24.png',
        'https://kitdls.net/wp-content/uploads/2024/09/Manchester-City-Kit-X-Kevin-De-Bruyne-DLS-24.png',
        'https://kitdls.net/wp-content/uploads/2024/08/Manchester-City-Away-Kit-V2-2024-2025-DLS-24.png',
        'https://kitdls.net/wp-content/uploads/2024/09/Manchester-City-Kit-X-Kevin-De-Bruyne-2-DLS-24.png',
        'https://kitdls.net/wp-content/uploads/2024/05/DLS-24-Manchester-City-Third-Kit-V2-2024-2025.png',
        'https://kitdls.net/wp-content/uploads/2025/02/Manchester-City-Four-Kits-2025-DLS-25.png',
        'https://kitdls.net/wp-content/uploads/2025/02/MC-GK-Kit-1-DLS-25.png',
        'https://kitdls.net/wp-content/uploads/2025/02/MC-GK-Kit-2-DLS-25.png',
        'https://kitdls.net/wp-content/uploads/2024/08/Manchester-City-GK-Home-Kit-2024-2025-DLS-24.png',
        'https://kitdls.net/wp-content/uploads/2024/08/Manchester-City-GK-Away-Kit-2024-2025-DLS-24.png',
        'https://kitdls.net/wp-content/uploads/2024/08/Manchester-City-GK-Third-Kit-2024-2025-DLS-24.png',
        'https://kitdls.net/wp-content/uploads/2024/05/DLS-24-Manchester-City-Dragon-Kit-2024.png',
        'https://kitdls.net/wp-content/uploads/2023/12/kit-manchester-city-home-2023-2024-dls-2024.png',
        'https://kitdls.net/wp-content/uploads/2023/12/kit-manchester-city-away-2023-2024-dls-2024.png',
        'https://kitdls.net/wp-content/uploads/2023/12/kit-manchester-city-third-2023-2024-dls-2024.png',
        'https://kitdls.net/wp-content/uploads/2023/12/kit-manchester-city-gk1-2023-2024-dls-2024.png',
        'https://kitdls.net/wp-content/uploads/2023/12/kit-manchester-city-gk3-2023-2024-dls-2024.png'
    ],
    'Al-Nasr': [
        'https://dlsgame.net/wp-content/uploads/2025/03/Al-Nassr-Home-Kit-25-DLS-25.png',
        'https://dlsgame.net/wp-content/uploads/2025/03/Al-Nassr-Away-Kit-25-DLS-25.png',
        'https://kitdls.net/wp-content/uploads/2024/05/Al-Nassr-Home-Kit-V2-2024-2025-DLS-24.png',
        'https://kitdls.net/wp-content/uploads/2024/08/Al-Nassr-Home-Kit-X-CR7.png',
        'https://kitdls.net/wp-content/uploads/2024/05/Al-Nassr-Away-Kit-V2-2024-2025-DLS-24.png',
        'https://kitdls.net/wp-content/uploads/2024/08/Al-Nassr-Away-Kit-X-CR7.png',
        'https://kitdls.net/wp-content/uploads/2024/03/Al-Nassr-Third-Kit-2024-2025-DLS-24.png',
        'https://kitdls.net/wp-content/uploads/2024/05/Al-Nassr-GK-Home-Kit-2024-2025-DLS-24.png',
        'https://kitdls.net/wp-content/uploads/2024/05/Al-Nassr-GK-Away-Kit-2024-2025-DLS-24.png',
        'https://kitdls.net/wp-content/uploads/2024/05/Al-Nassr-GK-Third-Kit-2024-2025-DLS-24.png',
        'https://kitdls.net/wp-content/uploads/2023/12/Kit-AL-Nassr-Home-2023-2024-DLS-24-1.png',
        'https://kitdls.net/wp-content/uploads/2023/12/Kit-AL-Nassr-Home-2023-2024-DLS-24-2.png',
        'https://kitdls.net/wp-content/uploads/2023/12/Kit-AL-Nassr-Away-2023-2024-DLS-24.png',
        'https://kitdls.net/wp-content/uploads/2023/12/Kit-AL-Nassr-GK-2023-2024-DLS-24.png'
    ],
    'Real Madrid': [
        'https://i.ibb.co/h8Z578f/image.png',
        'https://i.ibb.co/kg8W9YN/image.png',
        'https://kitdls.net/wp-content/uploads/2024/05/DLS-24-Real-Madrid-Home-Kit-V3-2024-2025.png',
        'https://kitdls.net/wp-content/uploads/2024/05/Kit-Real-Madrid-2024-2025-CR7-1.png',
        'https://kitdls.net/wp-content/uploads/2024/02/DLS-24-Real-Madrid-Third-Kit-2024-2025.png',
        'https://kitdls.net/wp-content/uploads/2024/05/DLS-24-Real-Madrid-Third-Kit-V2-2024-2025.png',
        'https://kitdls.net/wp-content/uploads/2024/09/DLS-24-Real-Madrid-GK-Kit-2024-2025.png',
        'https://kitdls.net/wp-content/uploads/2024/10/DLS-24-Real-Madrid-GK-Kit-2-2024-2025.png',
        'https://kitdls.net/wp-content/uploads/2024/10/DLS-24-Real-Madrid-GK-Kit-3-2024-2025.png',
        'https://kitdls.net/wp-content/uploads/2023/12/kit-real-madrid-home-2023-2024-dls-2024.png',
        'https://kitdls.net/wp-content/uploads/2023/12/kit-real-madrid-away-2023-2024-dls-2024.png',
        'https://kitdls.net/wp-content/uploads/2023/12/kit-real-madrid-third-2023-2024-dls-2024.png',
        'https://kitdls.net/wp-content/uploads/2023/12/kit-real-madrid-gk1-2023-2024-dls-2024.png',
        'https://kitdls.net/wp-content/uploads/2023/12/kit-real-madrid-gk2-2023-2024-dls-2024.png',
        'https://kitdls.net/wp-content/uploads/2023/12/kit-real-madrid-gk3-2023-2024-dls-2024.png',
        'https://kitdls.net/wp-content/uploads/2025/02/Real-Madrid-Home-Kit-2009-DLS-25.png',
        'https://kitdls.net/wp-content/uploads/2025/02/Real-Madrid-Away-Kit-2009-DLS-25.png',
        'https://kitdls.net/wp-content/uploads/2025/02/Real-Madrid-Third-Kit-2009-DLS-25.png',
        'https://kitdls.net/wp-content/uploads/2025/02/Real-Madrid-Home-Kit-2007-DLS-25.png',
        'https://kitdls.net/wp-content/uploads/2025/02/Real-Madrid-Away-Kit-2007-DLS-25.png',
        'https://kitdls.net/wp-content/uploads/2025/02/Real-Madrid-Third-Kit-2007-DLS-25.png',
        'https://kitdls.net/wp-content/uploads/2025/02/Real-Madrid-Home-Kit-2004-DLS-25.png',
        'https://kitdls.net/wp-content/uploads/2025/02/Real-Madrid-Third-Kit-2004-DLS-25.png',
        'https://kitdls.net/wp-content/uploads/2025/02/Real-Madrid-Home-Kit-2000-DLS-25.png',
        'https://kitdls.net/wp-content/uploads/2025/02/Real-Madrid-Away-Kit-2000-DLS-25.png',
        'https://kitdls.net/wp-content/uploads/2025/02/Real-Madrid-Third-Kit-2000-DLS-25.png'
    ],
    'Barcelona': [
        'https://dlsgame.net/wp-content/uploads/2025/04/Barcelona-Home-Kit-2005-06-DLS-25.png',
        'https://dlsgame.net/wp-content/uploads/2025/04/Barcelona-Away-Kit-2005-06-DLS-25.png',
        'https://kitdls.net/wp-content/uploads/2024/05/DLS-24-Barcelona-Home-Kit-V2-2024-2025.png',
        'https://kitdls.net/wp-content/uploads/2024/07/Barcelona-Home-Kit-2024-2025-DLS-24.png',
        'https://kitdls.net/wp-content/uploads/2024/07/Barcelona-Away-Kit-2024-2025-DLS-24.png',
        'https://kitdls.net/wp-content/uploads/2024/07/Barcelona-Third-Kit-2024-2025-DLS-24.png',
        'https://kitdls.net/wp-content/uploads/2024/07/Barcelona-Four-Kit-2024-2025-DLS-24.png',
        'https://kitdls.net/wp-content/uploads/2024/07/Barcelona-GK-Home-Kit-2024-2025-DLS-24.png',
        'https://kitdls.net/wp-content/uploads/2024/07/Barcelona-GK-Away-Kit-2024-2025-DLS-24.png',
        'https://kitdls.net/wp-content/uploads/2025/05/Barcelone-Home-Kit-X-Travis-Scott-DLS-25.png',
        'https://kitdls.net/wp-content/uploads/2025/05/Barcelone-Away-Kit-X-Travis-Scott-DLS-25.png',
        'https://kitdls.net/wp-content/uploads/2023/12/kit-barcelona-home-2023-2024-dls-2024.png',
        'https://kitdls.net/wp-content/uploads/2023/12/kit-barcelona-away-2023-2024-dls-2024.png',
        'https://kitdls.net/wp-content/uploads/2023/12/kit-barcelona-third-2023-2024-dls-2024.png',
        'https://kitdls.net/wp-content/uploads/2023/12/kit-barcelona-gk1-2023-2024-dls-2024.png',
        'https://kitdls.net/wp-content/uploads/2023/12/kit-barcelona-gk2-2023-2024-dls-2024.png',
        'https://kitdls.net/wp-content/uploads/2023/12/kit-barcelona-gk3-2023-2024-dls-2024.png',
        'https://kitdls.net/wp-content/uploads/2024/12/Barcelone-Home-Kit-2000-DLS-25.png',
        'https://kitdls.net/wp-content/uploads/2024/12/Barcelone-Away-Kit-2000-DLS-25.png',
        ],
     'Manchestr United': [
        # 1)
        'https://dlsgame.net/wp-content/uploads/2025/03/MU-Home-Kit-25-DLS-25.png',
        # 2)
        'https://dlsgame.net/wp-content/uploads/2025/03/MU-Away-Kit-25-DLS-25.png',
        # 3)
        'https://kitdls.net/wp-content/uploads/2024/02/DLS-24-MU-Home-Kit-2024-2025.png',
        'https://kitdls.net/wp-content/uploads/2024/08/Kit-MU-2024-CR7.png',
        'https://kitdls.net/wp-content/uploads/2024/02/DLS-24-MU-Away-Kit-2024-2025.png',
        'https://kitdls.net/wp-content/uploads/2024/08/Kit-MU-2024-CR7-2.png',
        'https://kitdls.net/wp-content/uploads/2024/02/DLS-24-MU-Third-Kit-2024-2025.png',
        'https://kitdls.net/wp-content/uploads/2024/08/DLS-24-MU-Third-Kit-V2-2024-2025.png',
        'https://kitdls.net/wp-content/uploads/2024/06/DLS-24-MU-GK-Home-Kit-2024-2025.png',
        'https://kitdls.net/wp-content/uploads/2024/06/DLS-24-MU-GK-Away-Kit-2024-2025.png',
        'https://kitdls.net/wp-content/uploads/2025/02/DLS-24-MU-GK-Third-Kit-2024-2025.png',
        'https://kitdls.net/wp-content/uploads/2023/12/Kit-Manchester-United-Home-2023-2024-DLS-2024-0.png',
        'https://kitdls.net/wp-content/uploads/2023/12/Kit-Manchester-United-Away-2023-2024-DLS-2024.png',
        'https://kitdls.net/wp-content/uploads/2023/12/Kit-Manchester-United-Third-2023-2024-DLS-2024.png',
        'https://kitdls.net/wp-content/uploads/2023/12/Kit-Manchester-United-GK1-2023-2024-DLS-2024.png',
        'https://kitdls.net/wp-content/uploads/2023/12/Kit-Manchester-United-GK2-2023-2024-DLS-2024.png',
        'https://kitdls.net/wp-content/uploads/2023/12/Kit-Manchester-United-GK3-2023-2024-DLS-2024.png',
        'https://kitdls.net/wp-content/uploads/2024/05/MU-Home-Kit-2007-2008-DLS-24.png',
        'https://kitdls.net/wp-content/uploads/2024/05/MU-Home-Kit-2-2007-2008-DLS-24.png',
        'https://kitdls.net/wp-content/uploads/2024/05/MU-Away-Kit-2007-2008-DLS-24.png',
        'https://kitdls.net/wp-content/uploads/2024/05/MU-GK-Kit-2007-2008-DLS-24.png',
        'https://kitdls.net/wp-content/uploads/2025/02/MU-Vodafone-1-Kit-25-DLS-25.png',
        'https://kitdls.net/wp-content/uploads/2025/02/MU-Vodafone-2-Kit-25-DLS-25.png',
        'https://kitdls.net/wp-content/uploads/2025/02/MU-Vodafone-3-Kit-25-DLS-25.png',
        'https://kitdls.net/wp-content/uploads/2025/02/MU-Vodafone-4-Kit-25-DLS-25.png'
    ],
}

# Foydalanuvchilarni yuklash
# Foydalanuvchilarni yuklash
env_user_verified = load_verified()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    username = update.effective_user.first_name or 'Foydalanuvchi'
    markup = ReplyKeyboardMarkup(MENU_BUTTONS, resize_keyboard=True)
    await update.message.reply_text(
        f'Assalomu alaykum, {username}!\nIltimos, menyudan tanlang:',
        reply_markup=markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Bosh menyuga qaytish tugmasi bilan yordam matni

    await update.message.reply_text(
        'Savollar bo‘lsa @sob1rov_00 ga yozing.',

    ),





async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    choice = update.message.text
    valid = [btn for row in MENU_BUTTONS for btn in row]

    if choice == 'Yordam':
        return await help_command(update, context)

    if choice in MEDIA_MAP:
        statuses = []
        for channel in REQUIRED_CHANNELS:
            try:
                member = await context.bot.get_chat_member(chat_id=channel, user_id=user_id)
                statuses.append(member.status in ['member', 'administrator', 'creator'])
            except Exception:
                statuses.append(False)

        if all(statuses):
            await send_media(context, user_id, choice)
        else:
            buttons = [[InlineKeyboardButton('Obuna bo‘lish', url=f'https://t.me/{ch[1:]}')] for ch in REQUIRED_CHANNELS]
            buttons.append([InlineKeyboardButton('✅ Obuna bo‘ldim', callback_data=f'check_subscription:{choice}')])
            reply_markup = InlineKeyboardMarkup(buttons)
            await update.message.reply_text(
                'Iltimos, kanallarga obuna bo‘lib, "✅ Obuna bo‘ldim" tugmasini bosing:',
                reply_markup=reply_markup
            )
    elif choice in valid:
        await update.message.reply_text(f'Siz tanladingiz: {choice}')
    else:
        await update.message.reply_text("Noma'lum variant. Qayta urinib ko'ring.")

async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global env_user_verified

    query = update.callback_query
    await query.answer()

    if query.data.startswith('check_subscription:'):
        _, choice = query.data.split(':', 1)

        unsubscribed_channels = []
        for channel in REQUIRED_CHANNELS:
            try:
                member = await context.bot.get_chat_member(chat_id=channel, user_id=query.from_user.id)
                is_sub = member.status in ['member', 'administrator', 'creator']
                if not is_sub:
                    unsubscribed_channels.append(channel)
            except Exception:
                unsubscribed_channels.append(channel)

        if query.from_user.id in env_user_verified and unsubscribed_channels:
            env_user_verified.remove(query.from_user.id)
            save_verified(env_user_verified)
            logger.info(f"❌ {query.from_user.id} ro'yxatdan olib tashlandi (kanaldan chiqib ketgan)")

        if not unsubscribed_channels:
            if query.from_user.id not in env_user_verified:
                env_user_verified.add(query.from_user.id)
                save_verified(env_user_verified)
                logger.info(f"➕ {query.from_user.id} ro'yxatga qo‘shildi")
            await query.message.reply_text("✅ Muvaffaqiyatli obuna bo‘ldingiz!")
            await send_media(context, query.from_user.id, choice)
        else:
            logger.info(f"🚫 Foydalanuvchi quyidagi kanallarga obuna emas: {unsubscribed_channels}")
            buttons = [
                [InlineKeyboardButton("Obuna bo‘lish", url=f'https://t.me/{ch[1:]}')] for ch in unsubscribed_channels
            ]
            buttons.append([InlineKeyboardButton("✅ Obuna bo‘ldim", callback_data=f'check_subscription:{choice}')])
            reply_markup = InlineKeyboardMarkup(buttons)
            await query.message.reply_text(
                'Iltimos, quyidagi kanal(lar)ga obuna bo‘ling va "✅ Obuna bo‘ldim" tugmasini bosing:',
                reply_markup=reply_markup
            )


async def send_media(context, user_id, choice):
    for url in MEDIA_MAP.get(choice, []):
        if url.startswith('https://t.me/'):
            await context.bot.send_message(chat_id=user_id, text=url)
        else:
            await context.bot.send_photo(chat_id=user_id, photo=url, caption=url)
        await asyncio.sleep(0.5)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("⚠️ Exception while handling an update:", exc_info=context.error)


def main() -> None:
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_choice))
    app.add_handler(CallbackQueryHandler(check_subscription))  # pattern removed to catch all
    app.add_error_handler(error_handler)

    logger.setLevel(logging.INFO)
    app.run_polling()

if __name__ == '__main__':
    main()




   #  ("https://i.ibb.co/h8Z578f/image.png", "https://i.ibb.co/h8Z578f/image.png"),
   #  ("https://i.ibb.co/kg8W9YN/image.png", "https://i.ibb.co/kg8W9YN/image.png"),
    # ("https://i.ibb.co/stDkGPs/image.png", "https://i.ibb.co/stDkGPs/image.png"),
   #  ("https://i.ibb.co/GR45jFN/image.png", "https://i.ibb.co/GR45jFN/image.png"),
    # ("https://i.ibb.co/ZVCLPJY/image.png", "https://i.ibb.co/ZVCLPJY/image.png"),

# git add requirements.txt
# git commit -m "Initial commit"
# git push