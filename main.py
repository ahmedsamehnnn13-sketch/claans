import random
import logging
import os
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from PIL import Image, ImageDraw, ImageFont

# إعداد السجلات لمراقبة البوت في Railway
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = "8419837789:AAEld-Nu02g66kjmYUlEfswBZpmhvhQGFao"

def create_image_no_file(matches, refs, version):
    """دالة رسم الصورة باستخدام خطوط النظام الافتراضية"""
    width, height = 800, 1100
    img = Image.new('RGB', (width, height), color=(15, 15, 15))
    draw = ImageDraw.Draw(img)
    
    # محاولة استخدام خطوط النظام الافتراضية في Railway (Linux)
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
    ]
    
    font = None
    for path in font_paths:
        if os.path.exists(path):
            font = ImageFont.truetype(path, 28)
            break
    if not font:
        font = ImageFont.load_default()

    # رسم الإطار الذهبي شبه التصميم المطلوب
    draw.rectangle([15, 15, 785, 1085], outline=(184, 134, 11), width=5)
    draw.text((220, 50), "THE STRONGEST CLAN", fill=(218, 165, 32), font=font)
    draw.text((330, 100), f"PHASE: {version}", fill=(255, 255, 255), font=font)
    
    y = 200
    for (m, r) in zip(matches, refs):
        draw.rectangle([60, y, 740, y+90], outline=(60, 60, 60), width=1)
        draw.text((280, y+15), f"{m[0]} VS {m[1]}", fill=(255, 255, 255), font=font)
        draw.text((280, y+50), f"REFEREE: {r}", fill=(0, 191, 255), font=font)
        y += 110

    path = "tournament_card.png"
    img.save(path)
    return path

async def handle_logic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    lines_all = [l.strip() for l in text.split('\n') if l.strip()]
    
    # استخراج رقم النسخة إذا وجد (رقم وحيد في سطر)
    version_id = "16"
    for line in lines_all:
        if line.isdigit() or (len(line) == 2 and line[0] == '¹'):
            version_id = line
            break

    # 1. حالة استلام القرعة مع الحكام لإخراج التصميم النهائي
    if "vs" in text.lower():
        lines = [l.strip() for l in text.split('\n') if "vs" in l.lower()]
        matches, refs = [], []
        
        for line in lines:
            clean_line = line.replace('•', '').strip()
            parts = clean_line.split('@')
            match_part = parts[0].strip()
            ref_part = "@" + parts[1].strip() if len(parts) > 1 else "@levil_8"
            
            teams = match_part.lower().split('vs')
            if len(teams) >= 2:
                matches.append((teams[0].strip().upper(), teams[1].strip().upper()))
                refs.append(ref_part)

        time_limit = (datetime.now() + timedelta(hours=14)).strftime('%I:%M %p')
        cliche = (
            "اسعد الله اوقاتكم بكل خير متابعين قنوات الاتحاد العربي للكلانات.\n"
            "─────✥─ ✺❀✺ ─✥─────\n\n"
            f"اليكم قرعة دور {version_id} من البطولة.\n\n"
            "⟿⟿⟿ ⤼ 𝗧𝗛𝗘 𝗧𝗢𝗨𝗥𝗡𝗔𝗠𝗘𝗡𝗧 ⤽ ⟿⟿⟿\n\n"
        )
        for m, r in zip(matches, refs):
            cliche += f". ◌  ⦃ {m[0]} ⦄ vs ⦃ {m[1]} ⦄ ◌ .\n𝗥𝗘𝗙 𒀭 𓌹 {r} 𓌺\n─────✥─ ✺❀✺ ─✥─────\n\n"
        
        cliche += f"𝒏𝒖𝒎𝒃𝒆𝒓 𝒐𝒇 𝒑𝒍𝒂𝒚𝒆𝒓𝒔 ➫ ❻⊷❻\n𝒍𝒐𝒃𝒃𝒚 𝒕𝒊𝒎𝒆 ➫ {time_limit}\n"
        cliche += "◊═━──┈─┈┉❀┉┈┈───━═◊"

        # إرسال الصورة والكليشة
        try:
            img_path = create_image_no_file(matches, refs, version_id)
            await update.message.reply_photo(photo=open(img_path, 'rb'), caption=cliche)
        except Exception as e:
            await update.message.reply_text(cliche)

        # إرسال رسالة "بيانات البطولة" المطلوبة
        info_msg = (
            "────── ••◦⊱≼≽⊰◦•• ──────\n"
            "                   بـيـانـات الـبـطـولـة\n"
            "────── ••◦⊱≼≽⊰◦•• ──────\n\n"
            f"اسـم الـبـطـولـة: THE Strongest clan {version_id}\n"
            "الـمـنـظـم : @levil_8\n"
            "مـنشـور دور 16 : \n"
            "مـنشـور دور الـربـع الـنـهـائـي : قريبا\n"
            "مـنشـور دور الـنـصـف الـنـهـائـي : قريبا\n"
            "مـنشـور دور  الـنـهـائـي : قريبا\n"
            "────── ••◦⊱≼≽⊰◦•• ──────"
        )
        await update.message.reply_text(info_msg)

    # 2. حالة استلام أسماء فقط لعمل القرعة الأولية
    else:
        clans = [l.strip() for l in lines_all if not l.isdigit() and '¹' not in l]
        if len(clans) < 2: return
        random.shuffle(clans)
        draw_res = "✅ تمت القرعة! انسخها وضف لها الحكام ثم أرسلها:\n\n"
        for i in range(0, len(clans)-1, 2):
            draw_res += f"• {clans[i]} vs {clans[i+1]} @يوزر_الحكم\n"
        await update.message.reply_text(draw_res)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_logic))
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
