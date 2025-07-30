import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters,
)
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_CHAT_ID = os.getenv("GROUP_CHAT_ID")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(_name_)

users = {}  # user_id -> {"balance": int, "bets": list}
matches = {
    1: {"teams": ["Team A", "Team B"], "coeffs": [1.5, 2.3], "status": "open"},
    2: {"teams": ["Team C", "Team D"], "coeffs": [1.8, 1.9], "status": "open"},
}  # example matches

MIN_BET = 10


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in users:
        users[user_id] = {"balance": 100, "bets": []}
        await update.message.reply_text(
            "Привет! Твой баланс 100 баллов. Используй /matches чтобы увидеть доступные игры."
        )
    else:
        await update.message.reply_text("Ты уже зарегистрирован. Используй /matches.")


async def matches_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "Доступные матчи для ставок:\n"
    for mid, m in matches.items():
        text += f"{mid}. {m['teams'][0]} vs {m['teams'][1]} | Коэффициенты: {m['coeffs'][0]}, {m['coeffs'][1]}\n"
    await update.message.reply_text(text)


async def bet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in users:
        await update.message.reply_text("Сначала используй /start для регистрации.")
        return
    try:
        mid = int(context.args[0])
        team_choice = context.args[1]
        bet_points = int(context.args[2])
    except (IndexError, ValueError):
        await update.message.reply_text("Использование: /bet <номер_матча> <команда_1|команда_2> <баллы>")
        return

    if mid not in matches or matches[mid]["status"] != "open":
        await update.message.reply_text("Такого матча нет или он закрыт.")
        return
    if team_choice not in ['1', '2']:
        await update.message.reply_text("Выберите команду: 1 или 2.")
        return
    if bet_points < MIN_BET:
        await update.message.reply_text("Ну ты лудик, всё проиграл? Минимум 10 баллов.")
        return
    if bet_points > users[user_id]["balance"]:
        await update.message.reply_text("Не не не дружок, у тебя не хватает баллов.")
        return

    # Сохраняем ставку
    users[user_id]["balance"] -= bet_points
    users[user_id]["bets"].append({"match_id": mid, "team": int(team_choice), "points": bet_points})

    await update.message.reply_text(f"Ставка принята: матч {mid}, команда {team_choice}, баллы {bet_points}.")


async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in users:
        await update.message.reply_text("Ты не зарегистрирован. Введи /start.")
        return
    bal = users[user_id]["balance"]
    await update.message.reply_text(f"Твой баланс: {bal} баллов.")


def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("matches", matches_cmd))
    application.add_handler(CommandHandler("bet", bet))
    application.add_handler(CommandHandler("balance", balance))

    application.run_polling()


if _name_ == '_main_':
    main()
