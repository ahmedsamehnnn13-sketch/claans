import random
import os
import logging
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from PIL import Image, ImageDraw, ImageFont

# إعدادات اللوج عشان تشوف البوت بيعمل إيه في Railway
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = "8520440293:AAH5tEodZxDeQL63-ry9mUxWWjmWUj1TRC0"

def create_tournament_image(matches):
    img = Image.new('RGB', (800, 600), color=(15, 15, 15))
    draw = ImageDraw.Draw(img)
    try:
        # بيحاول يدور على خط في النظام، لو ملحقتهوش بياخد الافتراضي
        font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()

    draw.text((250, 30), "Tournament Matches", fill=(255, 215, 0))
    y = 100
    for m in matches:
        draw.text((100, y), f"{m[0]}  VS  {m[1]}", fill=(255, 255, 255))
        y += 50
    img.save('match.png')
    return 'match.png'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("البوت شغال يا زعيم! ابعت رقم النسخة وتحتها الكلانات.")

async def handle_draw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    if len(lines) < 2:
        await update.message.reply_text("ابعت رقم النسخة في سطر والكلانات في أسطر تحتها.")
        return

    # استخراج رقم النسخة
    version_num = f"^{lines[0]}" if lines[0].isdigit() else "¹"
    clans = lines[1:] if lines[0].isdigit() else lines

    random.shuffle(clans)
    matches = [(clans[i], clans[i+1]) for i in range(0, len(clans) - 1, 2)]

    # حساب وقت اللوبي (14 ساعة من الآن)
    lobby_time = (datetime.now() + timedelta(hours=14)).strftime('%I:%M %p')

    cliche = (
        f"اسعد الله اوقاتكم بكل خير متابعين قنوات الاتحاد العربي للكلانات.\n"
        f"─────✥─ ✺❀✺ ─✥─────\n\n"
        f"اليكم قرعة دور 16 من البطولة {version_num}.\n\n"
        f"⟿⟿⟿ ⤼ 𝗧𝗛𝗘 𝗧𝗢𝗨𝗥𝗡𝗔𝗠𝗘𝗡𝗧 ⤽ ⟿⟿⟿\n\n"
    )

    for c1, c2 in matches:
        cliche += f". ◌  ⦃ {c1} ⦄ vs ⦃ {c2} ⦄ ◌ .\n𝗥𝗘𝗙 𒀭 𓌹 @        𓌺\n─────✥─ ✺❀✺ ─✥─────\n\n"

    cliche += f"𝒏𝒖𝒎𝒃𝒆𝒓 𝒐𝒇 𝒑𝒍𝒂𝒚𝒆𝒓𝒔 ➫ ❻⊷❻\n𝒍𝒐𝒃𝒃𝒚 𝒕𝒊𝒎𝒆 ➫ {lobby_time}\n"
    cliche += "◊═━──┈─┈┉❀┉┈┈───━═◊"

    try:
        img_path = create_tournament_image(matches)
        with open(img_path, 'rb') as photo:
            await update.message.reply_photo(photo=photo, caption=cliche)
    except Exception as e:
        # لو الصورة فشلت لأي سبب (زي نقص الخطوط) يبعت الكليشة نصاً عشان ميعلقش
        await update.message.reply_text(cliche)

def main():
    # drop_pending_updates=True دي مهمة جداً عشان ميردش على الرسايل القديمة اللي بعتها وهو مقفول
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_draw))
    
    print("البوت بدأ العمل...")
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
