import os
import tempfile
import uuid
import base64
import wave
from flask import Flask, request, abort
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from google import genai
from google.genai import types

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
WEBHOOK_BASE = os.environ["WEBHOOK_BASE"]
PORT = int(os.environ.get("PORT", "8080"))

env_keys = os.environ.get("GOOGLE_API_KEYS")
if env_keys:
    GOOGLE_API_KEYS = [k.strip() for k in env_keys.split(",") if k.strip()]

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

VOICES = [
    "Leda","Zephyr","Puck","Kore","Fenrir","Aoede",
    "Callirrhoe","Orus","Autonoe","Achernar"
]

user_voice = {}

def voice_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    row = []
    for v in VOICES:
        row.append(KeyboardButton(v))
        if len(row) == 2:
            kb.add(*row)
            row = []
    if row:
        kb.add(*row)
    return kb

def write_wav(path, pcm, rate=24000):
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(rate)
        wf.writeframes(pcm)

def generate_tts(text, voice):
    last_error = None
    for key in GOOGLE_API_KEYS:
        try:
            client = genai.Client(api_key=key)
            r = client.models.generate_content(
                model="gemini-2.5-flash-preview-tts",
                contents=text,
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name=voice
                            )
                        )
                    )
                )
            )
            p = r.candidates[0].content.parts[0].inline_data.data
            return base64.b64decode(p) if isinstance(p, str) else bytes(p)
        except Exception as e:
            last_error = e
    raise last_error

@bot.message_handler(commands=["start"])
def start(m):
    bot.send_message(
        m.chat.id,
        "Dooro codka aad rabto kadib ii soo dir qoraal",
        reply_markup=voice_keyboard()
    )

@bot.message_handler(func=lambda m: m.text in VOICES)
def set_voice(m):
    user_voice[m.from_user.id] = m.text
    bot.send_message(m.chat.id, f"Codka waa la beddelay: {m.text}")

@bot.message_handler(content_types=["text"])
def tts(m):
    voice = user_voice.get(m.from_user.id, "Leda")
    bot.send_chat_action(m.chat.id, "upload_audio")
    pcm = generate_tts(m.text, voice)
    path = os.path.join(
        tempfile.gettempdir(),
        f"{uuid.uuid4().hex}.wav"
    )
    write_wav(path, pcm)
    with open(path, "rb") as f:
        bot.send_audio(m.chat.id, f, caption=f"Voice: {voice}")
    os.remove(path)

@app.route("/", methods=["GET"])
def home():
    return "ok", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    if request.headers.get("content-type") == "application/json":
        update = telebot.types.Update.de_json(request.data.decode("utf-8"))
        bot.process_new_updates([update])
        return "", 200
    abort(403)

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_BASE.rstrip("/") + "/webhook")
    app.run(host="0.0.0.0", port=PORT)
