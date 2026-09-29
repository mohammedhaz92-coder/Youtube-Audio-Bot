import telebot
import yt_dlp
import os
from threading import Thread
from flask import Flask

# إعداد خادم الويب لإبقاء البوت متصلاً
app = Flask(__name__)

@app.route('/')
def index():
    return "البوت يعمل بنجاح!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# التوكن الخاص بك
TOKEN = "8985088016:AAG4DYONt_6mUpUVvQ-BAK4Qr1GP1zWwELY"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "مرحباً! أرسل لي أي رابط من يوتيوب وسأحوله لك إلى ملف MP3 🎵")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text
    if "youtube.com" not in url and "youtu.be" not in url:
        bot.reply_to(message, "الرجاء إرسال رابط يوتيوب صحيح.")
        return

    # إرسال رسالة تنبيه ببدء التحميل
    status_msg = bot.reply_to(message, "جاري التحميل والمعالجة... قد يستغرق الأمر بضع ثوانٍ ⏳")
    
    file_name = f"audio_{message.chat.id}_{message.message_id}"
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{file_name}.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'no_warnings': True
    }

    try:
        # تحميل المقطع
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        final_file = f"{file_name}.mp3"
        
        # إرسال الملف الصوتي للمستخدم
        with open(final_file, 'rb') as audio:
            bot.send_audio(message.chat.id, audio)
        
        # حذف رسالة "جاري التحميل" وحذف الملف من الخادم لتوفير المساحة
        bot.delete_message(message.chat.id, status_msg.message_id)
        os.remove(final_file)
        
    except Exception as e:
        bot.edit_message_text("حدث خطأ أثناء محاولة التحميل. تأكد من أن الرابط صحيح.", chat_id=message.chat.id, message_id=status_msg.message_id)

# تشغيل خادم الويب والبوت معاً
keep_alive()
bot.infinity_polling()
