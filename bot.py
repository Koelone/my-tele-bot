import os
import sqlite3
import threading
import time
from flask import Flask
import telebot

# Render အတွက် Port ပေးထားသည့် Flask Server
app = Flask(__name__)


@app.route("/")
def home():
  return "Bot is alive and running 24/7!"


def run_web():
  port = int(os.environ.get("PORT", 8080))
  app.run(host="0.0.0.0", port=port)


# Telegram Bot Setup
API_TOKEN = os.getenv("9177447395:AAFJfT0JKm_keDce-psByJrKm1Z2PPkIUmA")
ADMIN_ID = int(os.getenv("1627635151", "0"))

bot = telebot.TeleBot(API_TOKEN)

conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute(
    "CREATE TABLE IF NOT EXISTS subscribers (user_id INTEGER UNIQUE)"
)
conn.commit()


@bot.message_handler(commands=["start"])
def send_welcome(message):
  user_id = message.from_user.id
  cursor.execute(
      "INSERT OR IGNORE INTO subscribers (user_id) VALUES (?)", (user_id,)
  )
  conn.commit()
  bot.reply_to(message, "မင်္ဂလာပါ! Subscribe လုပ်ပြီးပါပြီ။")


@bot.message_handler(commands=["broadcast"])
def broadcast_message(message):
  if message.from_user.id != ADMIN_ID:
    return

  text_to_send = message.text.replace("/broadcast", "").strip()
  if not text_to_send:
    bot.reply_to(
        message, "ပို့မည့်စာသား ထည့်ပေးပါ (ဥပမာ- /broadcast မင်္ဂလာပါ)"
    )
    return

  cursor.execute("SELECT user_id FROM subscribers")
  users = cursor.fetchall()

  for user in users:
    try:
      bot.send_message(chat_id=user[0], text=text_to_send)
      time.sleep(0.05)
    except Exception:
      pass

  bot.reply_to(message, "စာများ အားလုံးဆီ ပို့ဆောင်ပြီးပါပြီ!")


if __name__ == "__main__":
  # Web server ကို နောက်ကွယ် (background thread) တွင် run ပေးထားခြင်း
  threading.Thread(target=run_web, daemon=True).start()
  print("Bot is starting polling...")
  bot.infinity_polling()
  
