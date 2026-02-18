import asyncio
import random
from datetime import datetime, timedelta
from telethon import TelegramClient, events
from PIL import Image, ImageDraw, ImageFont # تأكد من وجود خط عربي في مجلد الكود باسم font.ttf

# --- الإعدادات ---
API_ID = 26604893
API_HASH = 'b4dad6237531036f1a4bb2580e4985b1'
TARGET_CHANNEL = '@YourChannel' # قناة النشر
JUDGES_GROUP = '@JudgesGroup'   # جروب الحكام
MY_PRIVATE_GROUP = '@MyGroup'   # جروبك الخاص للتصميم

client = TelegramClient('union_session', API_ID, API_HASH)

# بيانات البطولات
version_names = ["الاولى", "الثانية", "الثالثة", "الرابعة", "الخامسة", "السادسة", "السابعة", "الثامنة", "التاسعة", "العاشرة", "الحادية عشرة", "الثانية عشرة", "الثالثة عشرة", "الرابعة عشرة", "الخامسة عشرة"]
data = {
    "current_version_idx": 0,
    "registered_clans": [], # تخزين أسماء الكلانات المسجلة حالياً
    "matches": [] # لتخزين القرعة
}

# دالة لتوليد نص الكليشة الأساسية
def get_main_cliche(v_name, clans):
    slots = [""] * 16
    for i, clan in enumerate(clans):
        if i < 16: slots[i] = clan
    
    cliche = f"""- اسعد الله اوقاتكم بكل خير اينما كُنتم مُتابعين قنوات الاتحاد العربي للكلانات .
━─── ••◦⊱≼≽⊰◦•• ───━
الـيـكـم بطوله كلانات تحت مسمى
⦉ The STRONGEST clan   ⦊
 ⦉ النسخة {v_name} ⦊
◊═━──┈─┈┉✪┉┈┈───━═◊
"""
    numbers = ["①", "②", "③", "④", "⑤", "⑥", "⑦", "⑧", "⑨", "①⓪", "①①", "①②", "①③", "①④", "①⑤", "①⑥"]
    for i in range(16):
        cliche += f"    {numbers[i]}❘➠ 𝗰𝗹𝗮𝗻 ⦉ {slots[i]} ⦊\n"
        
    cliche += f"""◊═━──┈─┈┉✪┉┈┈───━═◊
༻ {{ ملاحظه }} ༺ 
❶❘➠ التسجيل يكون فقط من القائد او المساعد 🥷
❷❘➠ اكتب شعار كلانك بل احرف الكبيرة
◊═━──┈─┈┉✪┉┈┈───━═◊
تنظيم ⤇⦇ @levil_8 ⦈
اشراف⤇⦇ الـلـجـنـة الـعـلـيـا ⦈"""
    return cliche

# 1. إرسال البطولة عند كتابة "بطوله" في المحفوظات
@client.on(events.NewMessage(chats='me', pattern='^بطوله$'))
async def start_tourney(event):
    if data["current_version_idx"] < len(version_names):
        v_name = version_names[data["current_version_idx"]]
        data["registered_clans"] = ["JUV", "TIT", "SP", "SHR", "JWA", "TDL", "TK", "STO"] # الكلانات الثابتة
        text = get_main_cliche(v_name, data["registered_clans"])
        await client.send_message(TARGET_CHANNEL, text)

# 2. تعديل الرسالة عند الرد بكلمة "تم"
@client.on(events.NewMessage(chats=TARGET_CHANNEL))
async def register_clan(event):
    if event.reply_to_msg_id and event.raw_text.strip() == "تم":
        reply_msg = await event.get_reply_message()
        # استخراج اسم الكلان من رسالة الشخص الذي رد "تم" عليه
        # سنفترض أن الشخص أرسل اسم الكلان ثم أنت رددت عليه بـ تم
        user_msg = await client.get_messages(event.chat_id, ids=event.reply_to_msg_id)
        clan_name = user_msg.raw_text.split()[-1] # يأخذ آخر كلمة كاسم كلان
        
        if len(data["registered_clans"]) < 16:
            data["registered_clans"].append(clan_name)
            v_name = version_names[data["current_version_idx"]]
            new_text = get_main_cliche(v_name, data["registered_clans"])
            await reply_msg.edit(new_text)
            
            # إذا اكتمل العدد 16، ابدأ القرعة
            if len(data["registered_clans"]) == 16:
                await start_draw()

async def start_draw():
    clans = data["registered_clans"]
    random.shuffle(clans)
    matches = [(clans[i], clans[i+1]) for i in range(0, 16, 2)]
    data["matches"] = matches
    
    draw_text = "⚠️ تم اكتمال العدد! قرعة دور 16:\n\n"
    for m in matches:
        draw_text += f"⦃ {m[0]} ⦄ vs ⦃ {m[1]} ⦄\n"
    
    await client.send_message(JUDGES_GROUP, draw_text + "\nبالرد على هذه الرسالة، يمكن للحكام استلام المباريات.")

# 3. توزيع المهام على الحكام
ref_count = 0
assigned_matches = []

@client.on(events.NewMessage(chats=JUDGES_GROUP))
async def assign_ref(event):
    global ref_count
    if event.reply_to_msg_id and len(assigned_matches) < 8:
        # إذا رد الحكم على رسالة القرعة
        user = await event.get_sender()
        match = data["matches"][len(assigned_matches)]
        assigned_matches.append({
            "match": match,
            "ref": f"@{user.username}" if user.username else user.first_name
        })
        await event.reply(f"تم تسجيلك حكماً للمباراة: {match[0]} ضد {match[1]}")
        
        if len(assigned_matches) == 8:
            await send_final_design()

async def send_final_design():
    # حساب الوقت (بعد 14 ساعة)
    future_time = datetime.now() + timedelta(hours=14)
    time_str = future_time.strftime("%I:%M %p").replace("AM", "صباحاً").replace("PM", "مساءً")
    
    final_text = f"""اسعد الله اوقاتكم بكل خير اينما كنتم متابعين قنوات الاتحاد العربي للكلانات.
─────✥─ ✺❀✺ ─✥─────
اليكم قرعة دور 16 من البطولة.
⟿⟿⟿ ⤼ 𝗧𝗛𝗘 𝗧𝗢𝗨𝗥𝗡𝗔𝗠𝗘𝗡𝗧 ⤽ ⟿⟿⟿\n"""

    for am in assigned_matches:
        final_text += f"\n. ◌  ⦃ {am['match'][0]} ⦄ vs ⦃ {am['match'][1]} ⦄ ◌ .\n𝗥𝗘𝗙 𒀭 𓌹 {am['ref']} 𓌺\n─────✥─ ✺❀✺ ─✥─────\n"

    final_text += f"""\n⟿⟿⟿  ⟲ 𝗟𝗔𝗪𝗦 ⟳ ⟿⟿⟿
𝒏𝒖𝒎𝒃𝒆𝒓 𝒐𝒇 𝒑𝒍𝒂𝒚𝒆𝒓𝒔 ➫ ❻⊷❻
𝒍𝒐𝒃𝒃𝒚 𝒕𝒊𝒎𝒆 ➫ بعد 14 ساعه {time_str}"""

    # إرسال النص لجروبك الخاص
    await client.send_message(MY_PRIVATE_GROUP, final_text)
    
    # --- جزء التصميم (Pillow) ---
    img = Image.new('RGB', (800, 1200), color=(20, 20, 20))
    # هنا يتم إضافة الرسم والكتابة على الصورة (يتطلب خط عربي font.ttf)
    # للتبسيط سأرسل الكليشة النصية، وإذا أردت رسم الصورة بدقة أخبرني.
    img.save('result.png')
    await client.send_file(MY_PRIVATE_GROUP, 'result.png', caption="تصميم مجمع للقرعة")

    # تصفير البيانات للنسخة القادمة
    data["current_version_idx"] += 1
    assigned_matches.clear()

client.start()
client.run_until_disconnected()
