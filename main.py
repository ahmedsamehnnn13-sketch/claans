import random
import logging
import os
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from PIL import Image, ImageDraw, ImageFont

# إعداد السجلات (Logs) لمراقبة البوت
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# التوكن الجديد والمصحح
TOKEN = "8419837789:AAEld-Nu02g66kjmYUlEfswBZpmhvhQGFao"

def create_tournament_image(matches):
    """دالة لإنشاء صورة المواجهات"""
    width, height = 800, 600
    img = Image.new('RGB', (width, height), color=(20, 20, 25))
    draw = ImageDraw.Draw(img)
    
    # محاولة استخدام خط للنظام، وإذا لم يوجد نستخدم الافتراضي
    try:
        # ملاحظة: في Railway يفضل رفع ملف خط باسم arial.ttf في مجلد البوت
        font = ImageFont.truetype("arial.ttf", 30)
    except:
        font = ImageFont.load_default()

    draw.text((250, 20), "TOURNAMENT DRAW", fill=(255, 215, 0))
    
    y = 80
    for i, (c1, c2) in enumerate(matches):
        match_text = f"{i+1}. {c1}  VS  {c2}"
        draw.text((100, y), match_text, fill=(255, 255, 255))
        y += 50
        if y > height - 50: break

    image_path = "match_result.png"
    img.save(image_path)
    return image_path

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """الرد على أمر /start"""
    await update.message.reply_text("✅ البوت جاهز! أرسل قائمة الكلانات (أول سطر رقم النسخة).")

async def handle_draw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الرسالة وعمل القرعة"""
    text = update.message.text.strip()
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    if len(lines) < 2:
        await update.message.reply_text("⚠️ يرجى إرسال القائمة بشكل صحيح.")
        return

    # استخراج النسخة والكلانات
    if lines[0].isdigit():
        version = f"^{lines[0]}"
        clans = lines[1:]
    else:
        version = "¹"
        clans = lines

    # عمل القرعة
    random.shuffle(clans)
    matches = [(clans[i], clans[i+1]) for i in range(0, len(clans) - 1, 2)]

    # حساب وقت اللوبي
    lobby_time = (datetime.now() + timedelta(hours=14)).strftime('%I:%M %p')

    # بناء الكليشة بالتنسيق المطلوب
    cliche = (
        "اسعد الله اوقاتكم بكل خير اينما كنتم متابعين قنوات الاتحاد العربي للكلانات.\n"
        "─────✥─ ✺❀✺ ─✥─────\n\n"
        f"اليكم قرعة دور 16 من البطولة {version}.\n\n"
        "⟿⟿⟿ ⤼ 𝗧𝗛𝗘 𝗧𝗢𝗨𝗥𝗡𝗔𝗠𝗘𝗡𝗧 ⤽ ⟿⟿⟿\n\n"
    )

    for c1, c2 in matches:
        cliche += f". ◌  ⦃ {c1} ⦄ vs ⦃ {c2} ⦄ ◌ .\n𝗥𝗘𝗙 𒀭 𓌹 @        𓌺\n─────✥─ ✺❀✺ ─✥─────\n\n"

    cliche += (
        "⟿⟿⟿  ⟲ 𝗟𝗔𝗪𝗦 ⟳ ⟿⟿⟿\n"
        "𝒏𝒖𝒎𝒃𝒆𝒓 𝒐𝒇 𝒑𝒍𝒂𝒚𝒆𝒓𝒔 ➫ ❻⊷❻\n"
        f"𝒍𝒐𝒃𝒃𝒚 𝒕𝒊𝒎𝒆 ➫ {lobby_time}\n"
        "◊═━──┈─┈┉❀┉┈┈───━═◊"
    )

    try:
        # محاولة إنشاء وإرسال الصورة
        path = create_tournament_image(matches)
        with open(path, 'rb') as photo:
            await update.message.reply_photo(photo=photo, caption=cliche)
    except Exception as e:
        # إذا حدث خطأ في مكتبة الصور، أرسل النص فقط لضمان عمل البوت
        logging.error(f"Error in image: {e}")
        await update.message.reply_text(cliche)

def main():
    # drop_pending_updates تتخلص من الرسائل القديمة المكتومة
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_draw))
    
    print("Bot is running...")
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
