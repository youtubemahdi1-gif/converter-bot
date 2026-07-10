import telebot
import os
import subprocess
import math
import traceback
from PIL import Image


# =========================
# CONFIG
# =========================

TOKEN = "7590925244:AAFj6uE8sFPEgx5K9J7WQG_Bslq9BD15Vxw"

bot = telebot.TeleBot(
    TOKEN,
    parse_mode="HTML"
)


# =========================
# TEMP
# =========================

TEMP_DIR = "temp"

if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)



# =========================
# START
# =========================

@bot.message_handler(commands=["start"])
def start(message):

    bot.reply_to(
        message,
        """
🤖 <b>ربات تبدیل فایل</b>

فایل را ارسال کنید.
بعد روی فایل ریپلای کنید و دستور تبدیل را بفرستید.

مثال:

گیف به استیکر
استیکر به عکس
عکس به استیکر
ویدیو به آهنگ
"""
    )



# =========================
# COMMANDS
# =========================

CONVERT_COMMANDS = {

    "گیف به استیکر": "gif_to_sticker",
    "گیف به ویدیو": "gif_to_video",
    "گیف به ویدئو": "gif_to_video",

    "استیکر به عکس": "sticker_to_photo",
    "استیکر به گیف": "sticker_to_gif",

    "عکس به استیکر": "photo_to_sticker",

    "ویدیو به گیف": "video_to_gif",
    "ویدئو به گیف": "video_to_gif",

    "ویدیو به استیکر": "video_to_sticker",
    "ویدئو به استیکر": "video_to_sticker",

    "ویدیو به آهنگ": "video_to_mp3",
    "ویدئو به آهنگ": "video_to_mp3",

    "png به jpg": "png_to_jpg",
    "jpg به png": "jpg_to_png"
}



# =========================
# FILE DETECT
# =========================

def get_file_info(message):

    if message.photo:
        return {
            "type": "photo",
            "id": message.photo[-1].file_id
        }

    if message.video:
        return {
            "type": "video",
            "id": message.video.file_id
        }

    if message.animation:
        return {
            "type": "gif",
            "id": message.animation.file_id
        }

    if message.sticker:
        return {
            "type": "sticker",
            "id": message.sticker.file_id
        }

    if message.document:
        return {
            "type": "document",
            "id": message.document.file_id
        }

    return None



# =========================
# DOWNLOAD
# =========================

def download_file(file_id, name):

    info = bot.get_file(file_id)

    data = bot.download_file(
        info.file_path
    )

    path = os.path.join(
        TEMP_DIR,
        name
    )

    with open(path, "wb") as f:
        f.write(data)

    return path



# =========================
# CLEAN
# =========================

def clean_temp():

    for f in os.listdir(TEMP_DIR):

        try:
            os.remove(
                os.path.join(
                    TEMP_DIR,
                    f
                )
            )

        except:
            pass

# =========================
# PHOTO TO STICKER
# =========================

def photo_to_sticker(path, chat_id):

    output = os.path.join(
        TEMP_DIR,
        "sticker.webp"
    )

    img = Image.open(path)

    img.thumbnail(
        (512, 512)
    )

    img.save(
        output,
        "WEBP"
    )

    with open(output, "rb") as f:

        bot.send_sticker(
            chat_id,
            f
        )

# =========================
# STICKER TO PHOTO
# =========================

def sticker_to_photo(path, chat_id):

    with open(path, "rb") as f:

        bot.send_photo(
            chat_id,
            f
        )



# =========================
# GET DURATION
# =========================

def get_duration(path):

    result = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            path
        ]
    )

    return float(result)



# =========================
# GIF TO VIDEO
# =========================

def gif_to_video(path, chat_id):

    output = os.path.join(
        TEMP_DIR,
        "gif_video.mp4"
    )

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            path,
            "-pix_fmt",
            "yuv420p",
            output
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )


    with open(output, "rb") as f:

        bot.send_video(
            chat_id,
            f
        )



# =========================
# VIDEO TO GIF
# =========================

def video_to_gif(path, chat_id):

    output = os.path.join(
        TEMP_DIR,
        "video.gif"
    )


    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            path,
            "-vf",
            "fps=15,scale=512:-1",
            output
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )


    with open(output, "rb") as f:

        bot.send_animation(
            chat_id,
            f
        )



# =========================
# GIF TO STICKER
# =========================

def gif_to_sticker(path, chat_id):

    output = os.path.join(
        TEMP_DIR,
        "gif.webp"
    )


    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            path,
            "-vf",
            "scale=512:512:force_original_aspect_ratio=decrease",
            "-c:v",
            "libwebp",
            "-loop",
            "0",
            output
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )


    with open(output, "rb") as f:

        bot.send_sticker(
            chat_id,
            f
        )

# =========================
# SPLIT VIDEO
# =========================

def split_video(path):

    duration = get_duration(path)

    parts = []

    count = math.ceil(duration / 3)


    for i in range(count):

        output = os.path.join(
            TEMP_DIR,
            f"video_{i}.webm"
        )


        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-ss",
                str(i * 3),
                "-i",
                path,
                "-t",
                "3",
                "-vf",
                "scale=512:512:force_original_aspect_ratio=decrease",
                "-c:v",
                "libvpx-vp9",
                "-an",
                output
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )


        parts.append(output)


    return parts



# =========================
# VIDEO TO STICKER
# =========================

def video_to_sticker(path, chat_id):

    duration = get_duration(path)


    if duration > 3:

        videos = split_video(path)

        for video in videos:

            with open(video, "rb") as f:

                bot.send_sticker(
                    chat_id,
                    f
                )

    else:

        output = os.path.join(
            TEMP_DIR,
            "video_sticker.webm"
        )


        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                path,
                "-t",
                "3",
                "-vf",
                "scale=512:512:force_original_aspect_ratio=decrease",
                "-c:v",
                "libvpx-vp9",
                "-an",
                output
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )


        with open(output, "rb") as f:

            bot.send_sticker(
                chat_id,
                f
            )



# =========================
# VIDEO TO MP3
# =========================

def video_to_mp3(path, chat_id):

    output = os.path.join(
        TEMP_DIR,
        "audio.mp3"
    )


    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            path,
            "-vn",
            "-codec:a",
            "libmp3lame",
            "-q:a",
            "2",
            output
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )


    with open(output, "rb") as f:

        bot.send_audio(
            chat_id,
            f
        )



# =========================
# PNG TO JPG
# =========================

def png_to_jpg(path, chat_id):

    output = os.path.join(
        TEMP_DIR,
        "image.jpg"
    )


    img = Image.open(path)

    img.convert(
        "RGB"
    ).save(
        output
    )


    with open(output, "rb") as f:

        bot.send_photo(
            chat_id,
            f
        )



# =========================
# JPG TO PNG
# =========================

def jpg_to_png(path, chat_id):

    output = os.path.join(
        TEMP_DIR,
        "image.png"
    )


    img = Image.open(path)

    img.save(
        output
    )


    with open(output, "rb") as f:

        bot.send_document(
            chat_id,
            f
        )

def sticker_to_gif(path, chat_id):

    output = os.path.join(
        TEMP_DIR,
        "sticker.gif"
    )

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            path,
            output
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    with open(output, "rb") as f:

        bot.send_animation(
            chat_id,
            f
        )

# =========================
# FINAL CONVERTER HANDLER
# =========================

@bot.message_handler(func=lambda m: True)
def converter(message):

    if not message.text:
        return


    command = message.text.strip().lower()


    if command not in CONVERT_COMMANDS:
        return


    if not message.reply_to_message:

        bot.reply_to(
            message,
            "❌ روی فایل موردنظر ریپلای کنید."
        )
        return



    info = get_file_info(
        message.reply_to_message
    )


    if not info:

        bot.reply_to(
            message,
            "❌ فایل پیدا نشد."
        )
        return



    action = CONVERT_COMMANDS[command]


    try:

        bot.reply_to(
            message,
            "⏳ در حال تبدیل..."
        )


        # عکس به استیکر
        if action == "photo_to_sticker":

            path = download_file(
                info["id"],
                "photo.jpg"
            )

            photo_to_sticker(
                path,
                message.chat.id
            )


        # استیکر به عکس
        elif action == "sticker_to_photo":

            path = download_file(
                info["id"],
                "sticker.webp"
            )

            sticker_to_photo(
                path,
                message.chat.id
            )

        # استیکر به گیف
        elif action == "sticker_to_gif":

            path = download_file(
                info["id"],
                "sticker.webp"
            )

            sticker_to_gif(
                path,
                message.chat.id
            )

        # گیف به استیکر
        elif action == "gif_to_sticker":

            path = download_file(
                info["id"],
                "gif.gif"
            )

            gif_to_sticker(
                path,
                message.chat.id
            )


        # گیف به ویدیو
        elif action == "gif_to_video":

            path = download_file(
                info["id"],
                "gif.gif"
            )

            gif_to_video(
                path,
                message.chat.id
            )


        # ویدیو به گیف
        elif action == "video_to_gif":

            path = download_file(
                info["id"],
                "video.mp4"
            )

            video_to_gif(
                path,
                message.chat.id
            )


        # ویدیو به استیکر
        elif action == "video_to_sticker":

            path = download_file(
                info["id"],
                "video.mp4"
            )

            video_to_sticker(
                path,
                message.chat.id
            )


        # ویدیو به آهنگ
        elif action == "video_to_mp3":

            path = download_file(
                info["id"],
                "video.mp4"
            )

            video_to_mp3(
                path,
                message.chat.id
            )


        # PNG به JPG
        elif action == "png_to_jpg":

            path = download_file(
                info["id"],
                "image.png"
            )

            png_to_jpg(
                path,
                message.chat.id
            )


        # JPG به PNG
        elif action == "jpg_to_png":

            path = download_file(
                info["id"],
                "image.jpg"
            )

            jpg_to_png(
                path,
                message.chat.id
            )


        else:

            bot.send_message(
                message.chat.id,
                "❌ این تبدیل هنوز فعال نشده."
            )


        clean_temp()


    except Exception as e:

        clean_temp()

        print(
            traceback.format_exc()
        )

        bot.reply_to(
            message,
            f"❌ خطا:\n{e}"
        )



# =========================
# RUN
# =========================

print("🤖 Converter Bot Started")

bot.infinity_polling(
    skip_pending=True
)
