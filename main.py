import random
import asyncio
from datetime import datetime, timedelta
from telethon import TelegramClient, events
from PIL import Image, ImageDraw, ImageFont
import io

# --- بياناتك الشخصية ---
API_ID = 26604893
API_HASH = 'b4dad6237531036f1a4bb2580e4985b1'

# --- المعرفات ---
TARGET_CHANNEL = '@clanaonq'   
JUDGES_GROUP = -1002029492622     
MY_PRIVATE_GROUP = -1003704705484  

v_names = ["الاولى", "الثانية", "الثالثة", "الرابعة", "الخامسة", "السادسة", "السابعة", "الثامنة", "التاسعة", "العاشرة", "الحادية عشرة", "الثانية عشرة", "الثالثة عشرة", "الرابعة عشرة", "الخامسة عشرة", "السادسة عشرة"]

state = {
    "v_idx": 8, # يبدأ من النسخة التاسعة
    "clans": [],
    "matches": [],
    "assigned_refs": {},
    "draw_msg_id": None
}

client = TelegramClient('bot_session', API_ID, API_HASH)

def create_design_image(v_name, matches, refs, time_str):
    # إنشاء صورة بخلفية سوداء (العرض 1000، الطول 1500)
    img = Image.new('RGB', (1000, 1600), color=(10, 10, 10))
    draw = ImageDraw.Draw(img)
    
    try:
        # تأكد من وجود ملف خط في نفس المجلد أو استخدم الخط الافتراضي
        font_title = ImageFont.load_default()
        font_match = ImageFont.load_default()
    except:
        font_title = ImageFont.load_default()
        font_match = ImageFont.load_default()

    # رسم العناوين
    draw.text((500, 100), f"النسخة {v_name}", fill=(255, 215, 0), anchor="mm")
    draw.text((500, 180), "THE STRONGEST CLAN", fill=(255, 255, 255), anchor="mm")
    
    y_pos = 300
    for i in range(1, 9):
        m = matches[i-1]
        r = refs[i]
        text_match = f"{m[0]} VS {m[1]}"
        text_ref = f"REF: {r}"
        
        # رسم إطار للمباراة
        draw.rectangle([100, y_pos, 900, y_pos+130], outline=(50, 50, 50), width=2)
        draw.text((500, y_pos+40), text_match, fill=(255, 255, 255), anchor="mm")
        draw.text((500, y_pos+90), text_ref, fill=(0, 200, 255), anchor="mm")
        y_pos += 150

    draw.text((500, 1500), f"LOBBY: {time_str} | 6 VS 6", fill=(255, 215, 0), anchor="mm")
    
    # حفظ الصورة في بايتس لإرسالها
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img_byte_arr

@client.on(events.NewMessage(chats='me', pattern='^بطوله$'))
async def start_handler(event):
    v_name = v_names[state["v_idx"]]
    # الكليشة العادية (تم اختصارها هنا لسهولة القراءة)
    msg = await client.send_message(TARGET_CHANNEL, f"تم بدء النسخة {v_name}")
    await event.reply(f"🚀 بدأت النسخة {v_name}")

@client.on(events.NewMessage(chats='me'))
async def list_handler(event):
    text = event.raw_text.strip()
    if "\n" in text:
        # نظام التعرف على النسخة بالسوبر سكريبت (كما في الكود السابق)
        lines = [line.strip() for line in text.split('\n') if line.strip()][:16]
        if len(lines) == 16:
            state["clans"] = lines
            state["assigned_refs"] = {}
            # توزيع القرعة
            clans_for_draw = lines[:]
            random.shuffle(clans_for_draw)
            state["matches"] = [(clans_for_draw[i], clans_for_draw[i+1]) for i in range(0, 16, 2)]
            
            # إرسال رسالة الحكام
            draw_msg = f"🔥 قرعة النسخة {v_names[state['v_idx']]}:\n"
            for i, m in enumerate(state["matches"], 1):
                draw_msg += f"{i}- {m[0]} vs {m[1]}\n"
            m = await client.send_message(JUDGES_GROUP, draw_msg + "\nرد برقم المباراة للاستلام")
            state["draw_msg_id"] = m.id

@client.on(events.NewMessage(chats=JUDGES_GROUP))
async def ref_handler(event):
    if event.reply_to_msg_id == state["draw_msg_id"]:
        num = event.raw_text.strip()
        if num.isdigit():
            idx = int(num)
            if 1 <= idx <= 8 and idx not in state["assigned_refs"]:
                user = await event.get_sender()
                ref_name = f"@{user.username}" if user.username else user.first_name
                state["assigned_refs"][idx] = ref_name
                await event.reply(f"✅ استلمت المباراة {idx}")
                
                if len(state["assigned_refs"]) == 8:
                    await send_final_report()

async def send_final_report():
    time_str = (datetime.now() + timedelta(hours=14)).strftime("%I:%M %p").replace("AM", "صباحاً").replace("PM", "مساءً")
    v_name = v_names[state["v_idx"]]
    
    # 1. تجهيز النص
    report_text = f"اسعد الله اوقاتكم... اليكم قرعة النسخة {v_name}.\n"
    for i in range(1, 9):
        m = state["matches"][i-1]
        r = state["assigned_refs"][i]
        report_text += f"\n. ◌  ⦃ {m[0]} ⦄ vs ⦃ {m[1]} ⦄ ◌ .\n𝗥𝗘𝗙: {r}\n─────✥─ ✺❀✺ ─✥─────\n"
    report_text += f"\n⟿⟿⟿  ⟲ 𝗟𝗔𝗪𝗦 ⟳ ⟿⟿⟿\n𝒏𝒖𝒎𝒃𝒆𝒓 𝒐𝒇 𝒑𝒍𝒂𝒚𝒆𝒓𝒔 ➫ ❻⊷❻\n𝒍𝒐𝒃𝒃𝒚 𝒕𝒊𝒎𝒆 ➫ بعد 14 ساعه {time_str}"

    # 2. توليد التصميم الصوري
    image_file = create_design_image(v_name, state["matches"], state["assigned_refs"], time_str)
    
    # 3. إرسال الصورة مع النص كـ Caption (ملصق مجمع)
    await client.send_file(MY_PRIVATE_GROUP, image_file, caption=report_text)
    
    state["v_idx"] += 1
    state["draw_msg_id"] = None

print("🚀 البوت يعمل بنظام التصميم المجمع...")
client.start()
client.run_until_disconnected()
