import os
import asyncio
import logging
import aiohttp
import aiofiles
import nest_asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatAction
import yt_dlp

nest_asyncio.apply()

API_ID = 29169428
API_HASH = "55742b16a85aac494c7944568b5507e5"
BOT1_TOKEN = "8441374183:AAGd6GFKfcNAPU8GC9bAkvZ9UvWkkgCnWhw"

DOWNLOAD_PATH = "downloads"
os.makedirs(DOWNLOAD_PATH, exist_ok=True)

COOKIES_TXT_CONTENT = """# Netscape HTTP Cookie File
.youtube.com	TRUE	/	FALSE	0	GPS	1
.youtube.com	TRUE	/	FALSE	0	APISID	Dmjbo61w5Or_L4vA/Acge0PIaJ8XjPLwJO
.youtube.com	TRUE	/	FALSE	0	HSID	AYWuTzsNICpoBgPoK
.youtube.com	TRUE	/	FALSE	0	SAPISID	ZlKXHrZg123F-624/AdMJxoBNKfZ48eJwM
.youtube.com	TRUE	/	FALSE	0	SID	g.a0003ggJHCAqDHJoE_E1Y5XV7kdfJzPFbYg9S-Qw8sNt9mCnxSGz4dNtAvisOCXE2oc5VO90wwACgYKAVsSARUSFQHGX2MiG2JUgsHKTnj3Fy53PdnzIxoVAUF8yKpWOazQ6A9POXdauZOJ9aR_0076
.youtube.com	TRUE	/	FALSE	0	SSID	Aromxb_20WnfMuoYA
.youtube.com	TRUE	/	FALSE	0	__Secure-1PAPISID	ZlKXHrZg123F-624/AdMJxoBNKfZ48eJwM
.youtube.com	TRUE	/	FALSE	0	__Secure-1PSID	g.a0003ggJHCAqDHJoE_E1Y5XV7kdfJzPFbYg9S-Qw8sNt9mCnxSGzqJ-T-qN-qEd6B5oFxBpGkAACgYKAdgSARUSFQHGX2MiAzIzraTcFR1LAI5aLQ3WDhoVAUF8yKoUw163E7K5Rl0zVZm9r63O0076
.youtube.com	TRUE	/	FALSE	0	__Secure-1PSIDTS	sidts-CjQBwQ9i59O7nZG1NsEwsF9FWHAhSWfBJ2GJl2eNLbWWwJfPVZRhMupROdMhg1SxIPC0GsVEAA
.youtube.com	TRUE	/	FALSE	0	__Secure-3PAPISID	ZlKXHrZg123F-624/AdMJxoBNKfZ48eJwM
.youtube.com	TRUE	/	FALSE	0	__Secure-3PSID	g.a0003ggJHCAqDHJoE_E1Y5XV7kdfJzPFbYg9S-Qw8sNt9mCnxSGzAXhVDacWNKGHAHBK-Na3NgACgYKAZQSARUSFQHGX2MimqnoKY7-1mxE6r84VXYrCRoVAUF8yKozFaD_VNmD033IhSU7N-uO0076
.youtube.com	TRUE	/	FALSE	0	__Secure-3PSIDTS	sidts-CjQBwQ9i59O7nZG1NsEwsF9FWHAhSWfBJ2GJl2eNLbWWwJfPVZRhMupROdMhg1SxIPC0GsVEAA
.youtube.com	TRUE	/	FALSE	0	__Secure-ROLLOUT_TOKEN	CO3i6YPBtsanChCbvJm5mJSPAxi_tpWwvP6QAw%3D%3D
.youtube.com	TRUE	/	FALSE	0	VISITOR_INFO1_LIVE	rEI5E-U0Jx0
.youtube.com	TRUE	/	FALSE	0	VISITOR_PRIVACY_METADATA	CgJTTxIEGgAgPw%3D%3D
.youtube.com	TRUE	/	FALSE	0	SIDCC	AKEyXzXYnfsZvXE83tZJzmdox-CJ2muTG4jBm8Cj5DcluoUV3bMbm8DPDtUiB5X0Zka5Aef4A
.youtube.com	TRUE	/	FALSE	0	LOGIN_INFO	AFmmF2swRAIgDZNVSUVBPG5jBs4vMtqddGswUyhxhIIsZdbOP2ELVJMCID7OMM2xPVgXGIaIZRZyBo8lagr1xwHqUysU66CAZejy:QUQ3MjNmeHFSZFlxNU1SVG84cWtzQk1fWVh1ek43WXduR1NPMnRTZEJzS3RCWFZWRjBwSGcyUUpIUWFxYkR6TnlBMXlDemdfYUFmZHFFa3BpcEVFMXB4SGxxQU8yTGR2bHNqQ2drMDkwRTVYZ1J6VGFVSUJMUjV6ZTlIdGRwWHhYR1h1ODdGNVR0WEVyZ2U2dzFNSW9iRVJUY0FlYXE5bkdB
.youtube.com	TRUE	/	FALSE	0	PREF	f6=40000000&tz=Africa.Mogadishu&f7=100&f5=30000
.youtube.com	TRUE	/	FALSE	0	YSC	oY9FuXuyEos"""

COOKIES_TXT_PATH = "cookies.txt"
with open(COOKIES_TXT_PATH, "w") as f:
    f.write(COOKIES_TXT_CONTENT)

YDL_OPTS = {
    "format": "best",
    "outtmpl": os.path.join(DOWNLOAD_PATH, "%(title)s.%(ext)s"),
    "noplaylist": True,
    "quiet": True,
    "cookiefile": COOKIES_TXT_PATH
}

SUPPORTED_DOMAINS = ["https://"]

class YTDLPLogger:
    def __init__(self):
        self._messages = []
    def debug(self, msg): self._messages.append(("DEBUG", str(msg)))
    def info(self, msg): self._messages.append(("INFO", str(msg)))
    def warning(self, msg): self._messages.append(("WARNING", str(msg)))
    def error(self, msg): self._messages.append(("ERROR", str(msg)))
    def text(self): return "\n".join(f"[{lvl}] {m}" for lvl, m in self._messages) if self._messages else ""

pyro_client = Client("youtube_downloader_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT1_TOKEN)

active_downloads = 0
queue = asyncio.Queue()
lock = asyncio.Lock()
BOT_USERNAME = None

async def get_bot_username(client):
    global BOT_USERNAME
    if BOT_USERNAME is None:
        try: BOT_USERNAME = (await client.get_me()).username
        except: return "Bot"
    return BOT_USERNAME

async def download_thumbnail(url, target_path):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(target_path, mode='wb')
                    await f.write(await resp.read())
                    await f.close()
                    if os.path.exists(target_path): return target_path
    except: pass
    return None

def extract_metadata_from_info(info):
    width = info.get("width")
    height = info.get("height")
    duration = info.get("duration")
    if not width or not height:
        formats = info.get("formats") or []
        best = next((f for f in formats if f.get("width") and f.get("height")), None)
        if best:
            width = width or best.get("width")
            height = height or best.get("height")
            duration = duration or best.get("duration") or (best.get("duration_ms")/1000 if best.get("duration_ms") else None)
    return width, height, duration

async def download_video(url: str, bot_username: str):
    loop = asyncio.get_running_loop()
    try:
        if not any(domain in url.lower() for domain in SUPPORTED_DOMAINS): return ("UNSUPPORTED",)
        ydl_opts = YDL_OPTS.copy()
        logger = YTDLPLogger()
        def extract_info_sync():
            with yt_dlp.YoutubeDL({**ydl_opts, "logger": logger}) as ydl: return ydl.extract_info(url, download=False)
        try: info = await loop.run_in_executor(None, extract_info_sync)
        except Exception as e: return ("YTDLP_ERROR", logger.text() or str(e))
        width, height, duration = extract_metadata_from_info(info)
        def download_sync():
            with yt_dlp.YoutubeDL({**ydl_opts, "logger": logger}) as ydl:
                info_dl = ydl.extract_info(url, download=True)
                return info_dl, ydl.prepare_filename(info_dl)
        try: info, filename = await loop.run_in_executor(None, download_sync)
        except Exception as e: return ("YTDLP_ERROR", logger.text() or str(e))
        title = info.get("title") or ""
        caption = title if len(title) <= 1024 else title[:1024]
        thumb = None
        if info.get("thumbnail"):
            thumb_path = os.path.splitext(filename)[0] + ".jpg"
            thumb = await download_thumbnail(info["thumbnail"], thumb_path)
        return caption, filename, width, height, duration, thumb
    except: return "ERROR"

async def _download_worker(client, message, url):
    bot_username = await get_bot_username(client)
    try: await client.send_chat_action(message.chat.id, ChatAction.TYPING)
    except: pass
    attempts, max_attempts = 0, 2
    while attempts < max_attempts:
        result = await download_video(url, bot_username)
        if result == "ERROR" or (isinstance(result, tuple) and result[0] in ("YTDLP_ERROR","UNSUPPORTED")):
            attempts += 1
            await asyncio.sleep(1)
            continue
        break
    if result is None or (isinstance(result, tuple) and result[0] in ("YTDLP_ERROR","UNSUPPORTED")):
        try: await message.reply("Error downloading video.")
        except: pass
        return
    if result == "ERROR":
        try: await message.reply("Error downloading video.")
        except: pass
        return
    caption, file_path, width, height, duration, thumb = result
    try: await client.send_chat_action(message.chat.id, ChatAction.UPLOAD_VIDEO)
    except: pass
    kwargs = {"video": file_path, "caption": caption, "supports_streaming": True}
    if width: kwargs["width"] = int(width)
    if height: kwargs["height"] = int(height)
    if duration: kwargs["duration"] = int(float(duration))
    if thumb and os.path.exists(thumb): kwargs["thumb"] = thumb
    kwargs["reply_to_message_id"] = message.id
    try: await client.send_video(message.chat.id, **kwargs)
    except: pass
    for f in [file_path, thumb]:
        if f and os.path.exists(f): os.remove(f)

async def download_task_wrapper(client, message, url):
    global active_downloads
    async with lock: active_downloads += 1
    try: await _download_worker(client, message, url)
    finally:
        async with lock: active_downloads -= 1
        while not queue.empty():
            c, m, u = await queue.get()
            asyncio.create_task(download_task_wrapper(c, m, u))

@pyro_client.on_message(filters.private & filters.command("start"))
async def start(client, message: Message):
    await message.reply("Welcome 👋\n\nThis bot downloads YouTube videos.\nSend a YouTube link to download the video.")

@pyro_client.on_message(filters.private & filters.text)
async def handle_link(client, message: Message):
    url = message.text.strip()
    if not any(domain in url.lower() for domain in SUPPORTED_DOMAINS):
        await message.reply("Please send a valid YouTube link 👍")
        return
    async with lock:
        asyncio.create_task(download_task_wrapper(client, message, url))

async def main():
    logging.getLogger().setLevel(logging.INFO)
    await pyro_client.start()
    while True:
        await asyncio.sleep(1000)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
