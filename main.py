import random
import logging
import os
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from PIL import Image, ImageDraw, ImageFont

# إعدادات اللوج
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = "8419837789:AAEld-Nu02g66kjmYUlEfswBZpmhvhQGFao"

# مخزن مؤقت لحفظ القرعة قبل إضافة الحكام
user_data_store = {}

def create_advanced_image(matches, refs, version):
    """دالة رسم الصورة الاحترافية شبه التصميم المطلوب"""
    width, height = 800, 1100
    img = Image.new('RGB', (width, height), color=(10, 10, 10))
    draw = ImageDraw.Draw(img)
    
    # محاولة تحميل الخط
    try:
        font_main = ImageFont.truetype("arial.ttf", 24)
        font_title = ImageFont.truetype("arial.ttf", 35)
    except:
        font_main = ImageFont.load_default()
        font_title = ImageFont.load_default()

    # رسم الإطار الذهبي
    draw.rectangle([10, 10, 790, 1090], outline=(184, 134, 11), width=3)
    
    # العناوين
    draw.text((width//2 - 100, 40), "THE STRONGEST CLAN", fill=(218, 165, 32), font=font_title)
    draw.text((width//2 - 60, 100), f"PHASE: {version}", fill=(255, 255, 255), font=font_main)
    draw.line([250, 140, 550, 140], fill=(218, 165, 32), width=2)

    y_offset = 180
    for i, (m, r) in enumerate(zip(matches, refs)):
        # رسم مستطيل المواجهة
        draw.rectangle([50, y_offset, 750, y_offset + 90], outline=(50, 50, 50), width=1)
        
        # أسماء الكلانات
        match_txt = f"{m[0]} VS {m[1]}"
        draw.text((width//2 - 50, y_offset + 20), match_text, fill=(255, 255, 255), font=font_main)
        
        # الحكم
        ref_txt = f"REFEREE: {r}"
        draw.text((width//2 - 60, y_offset + 55), ref_txt, fill=(0, 191, 255), font=font_main)
        
        y_offset += 110

    # التذييل
    footer = "SYSTEM: 6 VS 6 | DEADLINE: 14 HOURS"
    draw.text((width//2 - 150, 1030), footer, fill=(100, 100, 100), font=font_main)

    img_path = "final_card.png"
    img.save(img_path)
    return img_path

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("مرحباً بك في بوت الاتحاد! 🛡\n1. أرسل قائمة الكلانات لعمل القرعة.\n2. بعد القرعة، أرسل يوزرات الحكام (كل يوزر في سطر).")

async def handle_logic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text.strip()
    lines = [l.strip() for l in text.split('\n') if l.strip()]

    # المرحلة الأولى: عمل القرعة
    if user_id not in user_data_store or "matches" not in user_data_store[user_id]:
        if len(lines) < 2:
            await update.message.reply_text("أرسل قائمة الكلانات أولاً (كل اسم في سطر).")
            return
        
        version = lines[0] if lines[0].isdigit() else "16"
        clans = lines[1:] if lines[0].isdigit() else lines
        random.shuffle(clans)
        
        matches = [(clans[i], clans[i+1]) for i in range(0, len(clans)-1, 2)]
        user_data_store[user_id] = {"matches": matches, "version": version}
        
        res = "✅ تمت القرعة بنجاح:\n\n"
        for m in matches: res += f"• {m[0]} vs {m[1]}\n"
        res += "\nالآن أرسل قائمة يوزرات الحكام بنفس العدد."
        await update.message.reply_text(res)

    # المرحلة الثانية: إضافة الحكام وإخراج الكليشة والصورة
    else:
        matches = user_data_store[user_id]["matches"]
        version = user_data_store[user_id]["version"]
        
        if len(lines) < len(matches):
            await update.message.reply_text(f"محتاج {len(matches)} حكام، أنت أرسلت {len(lines)} فقط.")
            return
        
        refs = lines[:len(matches)]
        time_limit = (datetime.now() + timedelta(hours=14)).strftime('%I:%M %p')

        # إنشاء الكليشة
        cliche = (
            "اسعد الله اوقاتكم بكل خير متابعين قنوات الاتحاد العربي للكلانات.\n"
            "─────✥─ ✺❀✺ ─✥─────\n\n"
            f"اليكم قرعة دور {version} من البطولة.\n\n"
            "⟿⟿⟿ ⤼ 𝗧𝗛𝗘 𝗧𝗢𝗨𝗥𝗡𝗔𝗠𝗘𝗡𝗧 ⤽ ⟿⟿⟿\n\n"
        )
        for m, r in zip(matches, refs):
            cliche += f". ◌  ⦃ {m[0]} ⦄ vs ⦃ {m[1]} ⦄ ◌ .\n𝗥𝗘𝗙 𒀭 𓌹 {r} 𓌺\n─────✥─ ✺❀✺ ─✥─────\n\n"
        
        cliche += f"𝒏𝒖𝒎𝒃𝒆𝒓 𝒐𝒇 𝒑𝒍𝒂𝒚𝒆𝒓𝒔 ➫ ❻⊷❻\n𝒍𝒐𝒃𝒃𝒚 𝒕𝒊𝒎𝒆 ➫ {time_limit}\n"
        cliche += "◊═━──┈─┈┉❀┉┈┈───━═◊"

        # إنشاء الصورة
        try:
            path = create_advanced_image(matches, refs, version)
            with open(path, 'rb') as photo:
                await update.message.reply_photo(photo=photo, caption=cliche)
        except Exception as e:
            await update.message.reply_text(cliche)
        
        # مسح البيانات لبدء قرعة جديدة
        del user_data_store[user_id]

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_logic))
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
