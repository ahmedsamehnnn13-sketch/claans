import random
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from PIL import Image, ImageDraw, ImageFont

# توكن البوت الخاص بك
TOKEN = "8256105127:AAGRs0n6bGNJ74jXttJnh2Se0AnaW8kworQ"

# دالة لتوليد الصورة المجمعة
def create_tournament_image(matches):
    img = Image.new('RGB', (800, 600), color=(20, 20, 20))
    draw = ImageDraw.Draw(img)
    
    # يمكنك تحميل خط عربي هنا، سأستخدم الخط الافتراضي للتبسيط
    try:
        font = ImageFont.truetype("arial.ttf", 30)
    except:
        font = ImageFont.load_default()

    draw.text((300, 20), "Tournament Bracket", fill=(255, 215, 0), font=font)
    
    y_offset = 80
    for i, (c1, c2) in enumerate(matches):
        text = f"Match {i+1}: {c1} VS {c2}"
        draw.text((100, y_offset), text, fill=(255, 255, 255), font=font)
        y_offset += 60
        
    img.save('bracket.png')
    return 'bracket.png'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً بك! أرسل قائمة الكلانات (كل اسم في سطر) وسأقوم بعمل القرعة والكليشة.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    clans = [line.strip() for line in text.split('\n') if line.strip()]
    
    if len(clans) < 2:
        await update.message.reply_text("يرجى إرسال قائمة تحتوي على اسمين على الأقل.")
        return

    # خلط الكلانات وعمل القرعة
    random.shuffle(clans)
    matches = []
    for i in range(0, len(clans) - 1, 2):
        matches.append((clans[i], clans[i+1]))

    # حساب الوقت (14 ساعة من الآن)
    time_limit = (datetime.now() + timedelta(hours=14)).strftime('%I:%M %p')

    # بناء الكليشة
    cliche = "اسعد الله اوقاتكم بكل خير اينما كنتم متابعين قنوات الاتحاد العربي للكلانات.\n"
    cliche += "─────✥─ ✺❀✺ ─✥─────\n\n"
    cliche += "اليكم قرعة دور 16 من البطولة.\n\n"
    cliche += "⟿⟿⟿ ⤼ 𝗧𝗛𝗘 𝗧𝗢𝗨𝗥𝗡𝗔𝗠𝗘𝗡𝗧 ⤽ ⟿⟿⟿\n\n"

    for c1, c2 in matches:
        cliche += f". ◌  ⦃  {c1}  ⦄ vs ⦃  {c2}  ⦄ ◌ .\n"
        cliche += "𝗥𝗘𝗙 𒀭 𓌹 @        𓌺\n"
        cliche += "─────✥─ ✺❀✺ ─✥─────\n\n"

    cliche += f"⟿⟿⟿  ⟲ 𝗟𝗔𝗪𝗦 ⟳ ⟿⟿⟿\n"
    cliche += "𝒏𝒖𝒎𝒃𝒆𝒓 𝒐𝒇 𝒑𝒍𝒂𝒚𝒆𝒓𝒔 ➫ ❻⊷❻\n"
    cliche += f"𝒍𝒐𝒃𝒃𝒚 𝒕𝒊𝒎𝒆 ➫ حتى الساعة {time_limit}\n\n"
    cliche += "◊═━──┈─┈┉❀┉┈┈───━═◊"

    # توليد الصورة
    photo_path = create_tournament_image(matches)

    # إرسال الصورة والكليشة
    with open(photo_path, 'rb') as photo:
        await update.message.reply_photo(photo=photo, caption=cliche)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("البوت يعمل الآن...")
    app.run_polling()

if __name__ == '__main__':
    main()
