# bot.py
import json
import asyncio
import os
import base64
import logging
from typing import List, Optional, Tuple

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
)
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# ====== НАСТРОЙКИ ======
TOKEN = "8380517379:AAF1pCJKN2uz2YL86yw_wKcFHGy_oFmvOjQ"   # <-- подставь свой токен
LONG_DELETE_DELAY = 300      # 5 минут (удаление новых сообщений)
SHORT_DELETE_DELAY = 1       # 1 секунда (удаление старых при листании)
ITEMS_PER_PAGE = 4
PLACEHOLDER = "no_avatar.jpg"
LOG_FILE = "bot.log"

# ====== ЛОГИРОВАНИЕ ======
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler(LOG_FILE, encoding="utf-8")]
)
log = logging.getLogger(__name__)

# ====== Хранилище последних сообщений ======
# ключ: (chat_id, thread_id_or_None) -> list of bot message_ids
last_messages: dict[Tuple[int, Optional[int]], List[int]] = {}

# ====== Утилиты ======
def ensure_placeholder():
    if os.path.exists(PLACEHOLDER):
        return
    png_b64 = (
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGMAAQAABQAB"
        "DQottAAAAABJRU5ErkJggg=="
    )
    try:
        with open(PLACEHOLDER, "wb") as f:
            f.write(base64.b64decode(png_b64))
        log.info("Placeholder created: %s", PLACEHOLDER)
    except Exception as e:
        log.exception("Failed to create placeholder: %s", e)

def load_json(path: str):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        log.warning("Can't load JSON: %s", path)
        return []

def format_member(member: dict, index: int) -> str:
    profile = member.get("profile", "")
    display = member.get("display", "")
    diff = member.get("diff", 0)
    return (f"<b>{index}.</b> <a href='{profile}'>{display}</a>\n"
            f"<b>Прирост:</b> {diff:,} ⚡").replace(",", " ")

def get_avatar_path(member: dict) -> str:
    avatar = member.get("avatar", "")
    if avatar and os.path.isfile(avatar) and os.path.getsize(avatar) > 0:
        ext = os.path.splitext(avatar)[1].lower()
        if ext in (".jpg", ".jpeg", ".png"):
            return avatar
    return PLACEHOLDER

async def delete_messages(bot, chat_id: int, message_ids: List[int]):
    """Удаление сообщений. Для delete_message достаточно chat_id + message_id."""
    if not message_ids:
        return
    log.info("Deleting messages in chat=%s : %s", chat_id, message_ids)
    for mid in message_ids:
        try:
            await bot.delete_message(chat_id, mid)
            log.info("Deleted message %s in chat %s", mid, chat_id)
        except Exception as e:
            log.warning("Failed to delete message %s in chat %s: %s", mid, chat_id, e)

async def schedule_delete(bot, chat_id: int, message_ids: List[int], delay: float):
    await asyncio.sleep(delay)
    await delete_messages(bot, chat_id, message_ids)

# ====== ASCII картинки (можешь расширить) ======
ascii_art = {
    "КОТИК": """⣴⡿⠶⠀⠀⠀⣦⣀⣴⠀⠀⠀⠀
⣿⡄⠀⠀⣠⣾⠛⣿⠛⣷⠀⠿⣦ 
⠙⣷⣦⣾⣿⣿⣿⣿⣿⠟⠀⣴⣿
⠀⣸⣿⣿⣿⣿⣿⣿⣿⣾⠿⠋⠁
⠀⣿⣿⣿⠿⡿⣿⣿⡿⠀⠀⠀⠀
⢸⣿⡋⠀⠀⠀⢹⣿⡇⠀⠀⠀⠀
⣿⡟⠀⠀⠀⠀⠀⢿⡇""",
    "УТКА": """Утка
┈┈┈╱╱
┈┈╱╱╱▔
┈╱╭┈▔▔╲
▕▏┊╱╲┈╱▏
▕▏▕╮▕▕╮▏
▕▏▕▋▕▕▋▏
╱▔▔╲╱▔▔╲╮┈┈╱▔▔╲
▏▔▏┈┈▔┈┈▔▔▔╱▔▔╱
╲┈╲┈┈┈┈┈┈┈╱▔▔▔
┈▔╲╲▂▂▂▂▂╱
┈┈▕━━▏
┈┈▕━━▏
╱▔▔┈┈▔▔╲""",
    "ПИНГВИН": """．　　＿.＿
．　/######\\
． (##### @ ######\\
． /‘　\\######’ーー乛
．/　　\\####(
- /##　　'乛’ ＼
-/####\\　　　　\\
’/######\\
|#######　　　;
|########　　丿
|### '####　　/
|###　'###　 ;
|### 　##/　;
|###　''　　/
####　　／ 
/###　　乀
‘#/_______,)),）""",
    "СОБАКА": """╱▔▔╲▂▂▂╱▔▔╲
╲╱╳╱▔╲╱▔╲╱▔
┈┈┃▏▕▍▏▕▍▏
┈┈┃╲▂╱╲▂╱╲┈╭━╮
┈┈┃┊┳┊┊┊┊┊▔╰┳╯
┈┈┃┊╰━━━┳━━━╯
┈┈┃┊┊┊┊╭╯"""
}

# ====== Основная логика ======
async def send_page(origin, guild_key: str, page: int, context: ContextTypes.DEFAULT_TYPE, from_callback: bool):
    """
    origin: Update (команда) или CallbackQuery (нажатие кнопки)
    from_callback: True если перелистывание через кнопку
    """
    bot = context.bot

    # Загружаем актуальные данные каждый раз
    if guild_key == "ЕВ":
        data = load_json("history_ew.json")
    elif guild_key == "ЕД":
        data = load_json("history_ed.json")
    elif guild_key == "ТОП10":
        data = load_json("top10.json")
    else:
        data = []

    if not data:
        try:
            if hasattr(origin, "message") and origin.message:
                await origin.message.reply_text("Данные не найдены.")
            else:
                await origin.edit_message_text("Данные не найдены.")
        except Exception:
            pass
        return

    # Получаем chat и thread (для тем форума)
    if hasattr(origin, "message") and origin.message:
        chat = origin.message.chat
        chat_id = chat.id
        thread_id = getattr(origin.message, "message_thread_id", None)
    else:
        # запас
        chat_id = None
        thread_id = None

    key = (chat_id, thread_id)

    # Если перелистывание — запланировать быстрый удалитель старых сообщений
    if from_callback:
        old = last_messages.get(key)
        if old:
            # планируем удаление старых через SHORT_DELETE_DELAY
            asyncio.create_task(schedule_delete(bot, chat_id, old.copy(), SHORT_DELETE_DELAY))
            last_messages[key] = []

    new_ids: List[int] = []

    # подготовка kwargs для отправки в нужную тему (если есть thread_id)
    thread_kwargs = {"message_thread_id": thread_id} if thread_id is not None else {}

    try:
        if guild_key != "ТОП10":
            total_pages = max((len(data) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE, 1)
            page = page % total_pages
            start = page * ITEMS_PER_PAGE
            end = start + ITEMS_PER_PAGE
            members = data[start:end]

            # отправка медиа (аватарок)
            files = []
            try:
                # формируем media list
                media = []
                for m in members:
                    path = get_avatar_path(m)
                    f = open(path, "rb")
                    files.append(f)
                    media.append(InputMediaPhoto(media=f))
                # send_media_group с thread_kwargs
                msgs = await bot.send_media_group(chat_id=chat_id, media=media, **thread_kwargs)
                new_ids.extend([m.message_id for m in msgs])
            finally:
                for f in files:
                    try:
                        f.close()
                    except:
                        pass

            # подписи и кнопки (в отдельном сообщении)
            captions = [format_member(m, idx) for idx, m in enumerate(members, start=start + 1)]
            text_block = "\n\n".join(captions)

            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("⬅", callback_data=f"{guild_key}|{page-1}"),
                    InlineKeyboardButton("🔄", callback_data=f"{guild_key}|refresh|{page}"),
                    InlineKeyboardButton("➡", callback_data=f"{guild_key}|{page+1}")
                ]
            ])
            nav_msg = await bot.send_message(chat_id=chat_id, text=text_block, parse_mode="HTML",
                                             reply_markup=keyboard, **thread_kwargs)
            new_ids.append(nav_msg.message_id)

        else:
            # ТОП10 — текст без аватарок
            text = "🏆 <b>Топ 10 по вкладу</b> 🏆\n\n"
            for i, member in enumerate(data, start=1):
                text += f"{i}. <a href='{member.get('profile','')}'>{member.get('display','')}</a> — {member.get('diff',0):,} ⚡\n"
            text = text.replace(",", " ")
            msg_top = await bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML", **thread_kwargs)
            new_ids.append(msg_top.message_id)

    except Exception:
        log.exception("Failed to send page")

    # если вызов был текстом (не нажата кнопка) — удалим сообщение- команду пользователя через LONG_DELETE_DELAY
    try:
        is_callback = hasattr(origin, "data")
        if not is_callback and hasattr(origin, "message") and origin.message:
            user_cmd_mid = origin.message.message_id
            asyncio.create_task(schedule_delete(bot, chat_id, [user_cmd_mid], LONG_DELETE_DELAY))
    except Exception:
        log.exception("Error scheduling deletion of command msg")

    # сохранить id новых сообщений (чтобы при следующем перелистывании их удалить)
    last_messages[key] = new_ids.copy()

    # и планируем удаление этих новых сообщений через LONG_DELETE_DELAY
    try:
        asyncio.create_task(schedule_delete(bot, chat_id, new_ids.copy(), LONG_DELETE_DELAY))
        log.info("Scheduled long delete for new messages %s in chat %s", new_ids, chat_id)
    except Exception:
        log.exception("Failed to schedule long delete for new messages")

# ====== Хэндлеры ======
async def handle_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    text = update.message.text.strip().upper()

    if text in ("!ЕВ", "!ЕД", "!ТОП10"):
        guild_key = text.replace("!", "")
        log.info("Command %s from chat %s", text, update.message.chat.id)
        await send_page(update, guild_key, 0, context, from_callback=False)
        return
    
    # Новая фраза "иди нахуй"
    if text == "ИДИ НАХУЙ":
        msg = await update.message.reply_text("Сам иди нахуй")
        asyncio.create_task(schedule_delete(context.bot, update.message.chat.id,
                                            [update.message.message_id], LONG_DELETE_DELAY))
        asyncio.create_task(schedule_delete(context.bot, update.message.chat.id,
                                            [msg.message_id], LONG_DELETE_DELAY))
        return

    # Фраза "Буба" или "Buba"
    if text in ("БУБА", "BUBA"):
        msg = await update.message.reply_text("Не призывай сатану!")
        asyncio.create_task(schedule_delete(context.bot, update.message.chat.id,
                                            [update.message.message_id], LONG_DELETE_DELAY))
        asyncio.create_task(schedule_delete(context.bot, update.message.chat.id,
                                            [msg.message_id], LONG_DELETE_DELAY))
        return
    
    # ASCII команды — отправляются reply, поэтому автоматически в той же теме
    if text in ascii_art:
        msg = await update.message.reply_text(ascii_art[text])
        # удалить команду и ответ через LONG_DELETE_DELAY
        asyncio.create_task(schedule_delete(context.bot, update.message.chat.id, [update.message.message_id], LONG_DELETE_DELAY))
        asyncio.create_task(schedule_delete(context.bot, update.message.chat.id, [msg.message_id], LONG_DELETE_DELAY))
        return
    
async def page_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return
    await query.answer()
    data = query.data or ""
    if "|" not in data:
        return
    parts = data.split("|")
    guild_key = parts[0]
    if parts[1] == "refresh":
        # parts[2] contains page we were on — сохраним и остаёмся на той же странице
        page = int(parts[2]) if len(parts) > 2 else 0
        await send_page(query, guild_key, page, context, from_callback=True)
    else:
        page = int(parts[1])
        await send_page(query, guild_key, page, context, from_callback=True)

# ====== Запуск ======
def main():
    ensure_placeholder()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_command))
    app.add_handler(CallbackQueryHandler(page_callback))
    log.info("Bot started")
    app.run_polling()

if __name__ == "__main__":
    main()
