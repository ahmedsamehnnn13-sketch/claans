import random
import logging
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# تفعيل السجلات عشان نراقب البوت من ريلاوي
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# التوكن الجديد والمصحح
TOKEN = "8520440293:AAH5tEodZxDeQL63-ry9mUxWWjmWUj1TRC0"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("البوت اشتغل يا وحش! ابعت رقم النسخة وتحتها الكلانات.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lines = [line.strip() for line in update.message.text.split('\n') if line.strip()]
    
    if len(lines) < 2:
        await update.message.reply_text("ابعت رقم النسخة (مثلاً 1) في سطر، والكلانات في الأسطر اللي بعدها.")
        return

    # استخراج رقم النسخة
    ver = f"^{lines[0]}" if lines[0].isdigit() else "¹"
    clans = lines[1:] if lines[0].isdigit() else lines

    random.shuffle(clans)
    matches = [(clans[i], clans[i+1]) for i in range(0, len(clans) - 1, 2)]
    
    # حساب الوقت (14 ساعة من الآن)
    time_limit = (datetime.now() + timedelta(hours=14)).strftime('%I:%M %p')

    cliche = (
        f"اسعد الله اوقاتكم بكل خير متابعين قنوات الاتحاد العربي للكلانات.\n"
        f"─────✥─ ✺❀✺ ─✥─────\n\n"
        f"اليكم قرعة دور 16 من البطولة {ver}.\n\n"
        f"⟿⟿⟿ ⤼ 𝗧𝗛𝗘 𝗧𝗢𝗨𝗥𝗡𝗔𝗠𝗘𝗡𝗧 ⤽ ⟿⟿⟿\n\n"
    )

    for c1, c2 in matches:
        cliche += f". ◌  ⦃ {c1} ⦄ vs ⦃ {c2} ⦄ ◌ .\n𝗥𝗘𝗙 𒀭 𓌹 @        𓌺\n─────✥─ ✺❀✺ ─✥─────\n\n"

    cliche += f"𝒏𝒖𝒎𝒃𝒆𝒓 𝒐𝒇 𝒑𝒍𝒂𝒚𝒆𝒓𝒔 ➫ ❻⊷❻\n𝒍𝒐𝒃𝒃𝒚 𝒕𝒊𝒎𝒆 ➫ {time_limit}\n"
    cliche += "◊═━──┈─┈┉❀┉┈┈───━═◊"

    await update.message.reply_text(cliche)

def main():
    # drop_pending_updates بتمسح الرسايل القديمة اللي أنت بعتها والبوت واقف عشان ميهنجش
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("جاري تشغيل البوت...")
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
