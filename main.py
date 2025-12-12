import os
import asyncio
import time
from flask import Flask, request, abort
import telebot
import edge_tts
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, Update

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
WEBHOOK_URL_BASE = os.environ.get("WEBHOOK_URL_BASE", "https://texttospeechbbot.onrender.com")
PORT = int(os.environ.get("PORT", "8080"))
WEBHOOK_PATH = os.environ.get("WEBHOOK_PATH", "/webhook/")
WEBHOOK_URL = WEBHOOK_URL_BASE.rstrip('/') + WEBHOOK_PATH if WEBHOOK_URL_BASE else ""
DOWNLOADS_DIR = os.environ.get("DOWNLOADS_DIR", "./downloads")
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

bot = telebot.TeleBot(BOT_TOKEN, threaded=False)
flask_app = Flask(__name__)

CURRENT_VOICE_NAME = "so-SO-MuuseNeural"
CURRENT_VOICE_LABEL = "Muuse 👨🏻‍🦱"

def generate_tts_filename():
    return os.path.join(DOWNLOADS_DIR, f"tts_output_{int(time.time()*1000)}.mp3")

def create_voice_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    keyboard.add(KeyboardButton("Ubax 👩🏻‍🦳"), KeyboardButton("Muuse 👨🏻‍🦱"))
    return keyboard

@bot.message_handler(commands=["start"])
def start(message):
    keyboard = create_voice_keyboard()
    bot.send_message(
        message.chat.id,
        f"Text to Speech bot waa bilaabmay! Codka hadda la doortay waa: {CURRENT_VOICE_LABEL}.\n\nQoraal ii soo dir si aan cod ugu badalo.",
        reply_markup=keyboard,
        reply_to_message_id=message.message_id
    )

@bot.message_handler(func=lambda m: m.text in ["Ubax 👩🏻‍🦳", "Muuse 👨🏻‍🦱"])
def set_voice(message):
    global CURRENT_VOICE_NAME, CURRENT_VOICE_LABEL
    choice = message.text
    if "Ubax" in choice:
        CURRENT_VOICE_NAME = "so-SO-UbaxNeural"
        CURRENT_VOICE_LABEL = "Ubax 👩🏻‍🦳"
    elif "Muuse" in choice:
        CURRENT_VOICE_NAME = "so-SO-MuuseNeural"
        CURRENT_VOICE_LABEL = "Muuse 👨🏻‍🦱"
    bot.send_message(
        message.chat.id,
        f"Hadda waxaa la doortay codka: {CURRENT_VOICE_LABEL}.",
        reply_to_message_id=message.message_id
    )

@bot.message_handler(func=lambda m: True, content_types=['text'])
def handle_text(message):
    text = message.text.replace(".", "،")
    voice_name = CURRENT_VOICE_NAME
    filename = generate_tts_filename()

    async def make_tts():
        tts = edge_tts.Communicate(text, voice_name)
        await tts.save(filename)

    try:
        asyncio.run(make_tts())
        with open(filename, "rb") as voice:
            bot.send_voice(
                message.chat.id,
                voice,
                reply_to_message_id=message.message_id
            )
    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"Error: {e}",
            reply_to_message_id=message.message_id
        )
    finally:
        try:
            if os.path.exists(filename):
                os.remove(filename)
        except:
            pass

@flask_app.route("/", methods=["GET"])
def index():
    return "Bot Running💗", 200

@flask_app.route(WEBHOOK_PATH, methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        raw = request.get_data().decode('utf-8')
        bot.process_new_updates([Update.de_json(raw)])
        return '', 200
    abort(403)

if __name__ == "__main__":
    if WEBHOOK_URL:
        bot.remove_webhook()
        time.sleep(0.5)
        bot.set_webhook(url=WEBHOOK_URL)
        flask_app.run(host="0.0.0.0", port=PORT)
    else:
        print("Webhook URL not set, exiting.")
