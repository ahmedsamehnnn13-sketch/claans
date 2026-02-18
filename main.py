import random
import os
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from PIL import Image, ImageDraw, ImageFont

# التوكن الجديد اللي بعته
TOKEN = "8520440293:AAH5tEodZxDeQL63-ry9mUxWWjmWUj1TRC0"

def create_tournament_image(matches):
    img = Image.new('RGB', (800, 600), color=(15, 15, 15))
    draw = ImageDraw.Draw(img)
    try:
        # لو رفعت خط عربي سميه 'font.ttf' في ملفاتك
        font = ImageFont.truetype("arial.ttf", 25)
    except:
        font = ImageFont.load_default()

    draw.text((250, 30), "Tournament Matches", fill=(255, 215, 0), font=font)
    
    y = 100
    for m in matches:
        draw.text((100, y), f"{m[0]}  VS  {m[1]}", fill=(255, 255, 255), font=font)
        y += 50
    
    img.save('match.png')
    return 'match.png'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً بك! أرسل قائمة الكلانات وابدأ أول سطر برقم النسخة (مثلاً: 1).")

async def handle_draw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lines = [line.strip() for line in update.message.text.split('\n') if line.strip()]
    
    # استخراج رقم النسخة إذا وجد في أول سطر
    version_num = "¹"
    if lines[0].isdigit():
        version_num = f"^{lines[0]}"
        clans = lines[1:]
    else:
        clans = lines

    if len(clans) < 2:
        await update.message.reply_text("يا بطل محتاج على الأقل كلانين عشان أعمل قرعة!")
        return

    random.shuffle(clans)
    matches = [(clans[i], clans[i+1]) for i in range(0, len(clans) - 1, 2)]

    # حساب وقت اللوبي (14 ساعة من الآن)
    lobby_time = (datetime.now() + timedelta(hours=14)).strftime('%I:%M %p')

    cliche = f"اسعد الله اوقاتكم بكل خير اينما كنتم متابعين قنوات الاتحاد العربي للكلانات.\n"
    cliche += f"─────✥─ ✺❀✺ ─✥─────\n\n"
    cliche += f"اليكم قرعة دور 16 من البطولة {version_num}.\n\n"
    cliche += "⟿⟿⟿ ⤼ 𝗧𝗛𝗘 𝗧𝗢𝗨𝗥𝗡𝗔𝗠𝗘𝗡𝗧 ⤽ ⟿⟿⟿\n\n"

    for c1, c2 in matches:
        cliche += f". ◌  ⦃ {c1} ⦄ vs ⦃ {c2} ⦄ ◌ .\n"
        cliche += "𝗥𝗘𝗙 𒀭 𓌹 @        𓌺\n"
        cliche += "─────✥─ ✺❀✺ ─✥─────\n\n"

    cliche += f"⟿⟿⟿  ⟲ 𝗟𝗔𝗪𝗦 ⟳ ⟿⟿⟿\n"
    cliche += "𝒏𝒖𝒎𝒃𝒆𝒓 𝒐𝒇 𝒑𝒍𝒂𝒚𝒆𝒓𝒔 ➫ ❻⊷❻\n"
    cliche += f"𝒍𝒐𝒃𝒃𝒚 𝒕𝒊𝒎𝒆 ➫ {lobby_time}\n\n"
    cliche += "◊═━──┈─┈┉❀┉┈┈───━═◊"

    img_path = create_tournament_image(matches)
    with open(img_path, 'rb') as photo:
        await update.message.reply_photo(photo=photo, caption=cliche)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_draw))
    app.run_polling()

if __name__ == '__main__':
    main()
