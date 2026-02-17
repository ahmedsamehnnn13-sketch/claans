import telebot
import random
import re
import time
import io
from PIL import Image, ImageDraw, ImageFont

# --- الإعدادات الأساسية المعدلة ---
TOKEN = '8113358654:AAF6crTuiDikhfQz56twot-1vGs7exwdaTQ'
OWNER_USERNAME = 'levil_8'
TOURNAMENT_CHANNEL = "@botolaaatt" 
REF_GROUP_ID = -1003875646314      
PHOTO_URL = "https://i.ibb.co/Vp8pX0D/1000015262.jpg" 

bot = telebot.TeleBot(TOKEN)

class Tournament:
    def __init__(self):
        self.active = False
        self.stage = 16
        self.clans = []
        self.matches = []
        self.ref_assignments = {} 
        self.winners = []
        self.registration_msg_id = None
        self.draw_msg_id = None 
        self.klisha_sent = False
        self.photo_id = None

tourney = Tournament()

# --- دالة توليد تصميم صورة المواجهة باستخدام Pillow ---
def create_match_image(c1, c2, ref, stage_name):
    # إنشاء خلفية سوداء (800x450) بتصميم رياضي
    img = Image.new('RGB', (800, 450), color=(15, 15, 15))
    draw = ImageDraw.Draw(img)
    
    # رسم إطار مزدوج ذهبي وفضي لإعطاء هيبة
    draw.rectangle([10, 10, 790, 440], outline=(212, 175, 55), width=4) # ذهبي
    draw.rectangle([20, 20, 780, 430], outline=(192, 192, 192), width=1) # فضي
    
    try:
        # ملاحظة: الاستضافات تستخدم الخط الافتراضي إذا لم يتوفر ملف .ttf
        # يفضل دائماً رفع ملف خط Arial.ttf بجانب الكود واستخدامه
        font = ImageFont.load_default()
        
        # العنوان العلوي (المرحلة)
        draw.text((400, 60), f"TOURNEY: {stage_name}", fill=(255, 255, 255), anchor="mm")
        
        # أسماء الكلانات (يسار ويمين)
        draw.text((200, 225), c1, fill=(255, 255, 255), anchor="mm")
        draw.text((400, 225), "VS", fill=(212, 175, 55), anchor="mm")
        draw.text((600, 225), c2, fill=(255, 255, 255), anchor="mm")
        
        # الحكم المسؤول في الأسفل
        draw.text((400, 380), f"REFEREE: {ref}", fill=(0, 200, 255), anchor="mm")
    except:
        pass

    # حفظ الصورة في الذاكرة المؤقتة (Bytes) لإرسالها فوراً
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img_byte_arr

# دالة إرسال الصورة أو نص عند الفشل
def safe_send(chat_id, caption, custom_photo=None):
    try:
        if custom_photo:
            return bot.send_photo(chat_id, custom_photo, caption=caption)
        elif tourney.photo_id:
            return bot.send_photo(chat_id, tourney.photo_id, caption=caption)
        else:
            msg = bot.send_photo(chat_id, PHOTO_URL, caption=caption)
            tourney.photo_id = msg.photo[-1].file_id
            return msg
    except Exception as e:
        print(f"Error in safe_send: {e}")
        return bot.send_message(chat_id, caption)

def get_reg_text():
    slots = [" "] * 16
    for i in range(len(tourney.clans)):
        if i < 16: slots[i] = tourney.clans[i]
    icons = ["①","②","③","④","⑤","⑥","⑦","⑧","⑨","①⓪","①①","①②","①③","①④","①⑤","①⑥"]
    list_txt = "".join([f"    {icons[i]}❘➠ 𝗰𝗹𝗮𝗻 ⦉ {slots[i]} ⦊\n" for i in range(16)])
    return f"""- اسعد الله اوقاتكم بكل خير... مُتابعين قنوات الاتحاد العربي.
━─── ••◦⊱≼≽⊰◦•• ───━
الـيـكـم بطوله ⦉ THE STRONGEST CLAN ⦊
{list_txt}
تنظيم ⤇⦇ البوت المنظم ⦈
اشراف⤇⦇ الـلـجـنـة الـعـلـيـا ⦈"""

# --- أوامر التحكم ---
@bot.message_handler(func=lambda m: m.chat.type == 'private' and "بطوله" in m.text)
def start_tour(message):
    if message.from_user.username and message.from_user.username.lower() != OWNER_USERNAME.lower():
        return
    
    tourney.active, tourney.stage, tourney.clans = True, 16, []
    tourney.winners, tourney.ref_assignments, tourney.klisha_sent = [], {}, False
    
    msg = safe_send(TOURNAMENT_CHANNEL, get_reg_text())
    tourney.registration_msg_id = msg.message_id
    bot.reply_to(message, "✅ تم تفعيل وضع البطولة. بانتظار اكتمال القائمة في القناة.")

# --- استقبال الكلانات ---
@bot.message_handler(func=lambda m: tourney.active and tourney.stage == 16 and len(tourney.clans) < 16)
def register(message):
    if message.text.startswith('/') or "بطوله" in message.text: return
    
    name = message.text.strip().upper()
    if re.match(r"^[A-Z0-9]{2,8}$", name):
        if name in tourney.clans: return
        tourney.clans.append(name)
        bot.reply_to(message, f"✅ تم تسجيل {name} ({len(tourney.clans)}/16)")
        
        try:
            bot.edit_message_caption(get_reg_text(), TOURNAMENT_CHANNEL, tourney.registration_msg_id)
        except:
            pass
            
        if len(tourney.clans) == 16:
            start_draw_phase()

# --- القرعة ---
def start_draw_phase():
    random.shuffle(tourney.clans)
    tourney.matches = [[tourney.clans[i], tourney.clans[i+1]] for i in range(0, len(tourney.clans), 2)]
    
    stage_name = "FINAL" if tourney.stage == 2 else f"ROUND OF {tourney.stage}"
    bot.send_message(REF_GROUP_ID, f"📊 **تم توليد قرعة {stage_name}**\nيرجى حجز المباريات بالرد على الرقم:")
    
    send_ref_list()

def send_ref_list():
    txt = f"مواجهات {tourney.stage}:\n"
    for i, m in enumerate(tourney.matches):
        ref = tourney.ref_assignments.get(i+1, "متاح ✅")
        ref_tag = f"@{ref}" if ref != "متاح ✅" else ref
        txt += f"{i+1}- {m[0]} vs {m[1]} ⇇ {ref_tag}\n"
    bot.send_message(REF_GROUP_ID, txt)

@bot.message_handler(func=lambda m: m.chat.id == REF_GROUP_ID and m.reply_to_message)
def pick_match(message):
    try:
        num = int(re.search(r'\d+', message.text).group())
        if num in range(1, len(tourney.matches) + 1) and num not in tourney.ref_assignments:
            tourney.ref_assignments[num] = message.from_user.username
            bot.reply_to(message, f"✅ حجزت المواجهة رقم {num}")
            
            if len(tourney.ref_assignments) == len(tourney.matches) and not tourney.klisha_sent:
                tourney.klisha_sent = True
                post_final_draw()
    except: pass

def post_final_draw():
    stage_name = "FINAL" if tourney.stage == 2 else f"ROUND OF {tourney.stage}"
    
    if tourney.stage == 2:
        c1, c2 = tourney.matches[0][0], tourney.matches[0][1]
        ref = tourney.ref_assignments.get(1, "None")
        txt = f"""⭐️الان وصلنا وأياكم الى قمة النهائي المرتقب الذي يجمع مـا بين كلان {c2} و {c1}
من سيخطف لقب النسخة اولى ؟ 

وهي البـطوله العريقة جداً

🔤🤩 THE STRONGEST CLAN - 1 🤩🔤

📍 {c2} 🆚 {c1} 📍

REFEREE 👾 @{ref}
➖➖➖➖➖➖➖➖➖➖
- المنـظم 👾 بـوت الـمـنـظـمـيـن 🤍.
- المشرف 👾 اللجنه العليا  ❤️‍🔥.."""
        match_img = create_match_image(c1, c2, f"@{ref}", "GRAND FINAL")
        bot.send_photo(TOURNAMENT_CHANNEL, match_img, caption=txt)
    else:
        for i, m in enumerate(tourney.matches):
            ref = tourney.ref_assignments.get(i+1, "None")
            match_txt = f"⦃ {m[0]} ⦄ vs ⦃ {m[1]} ⦄\n𝗥𝗘𝗙: @{ref}\n──────"
            match_img = create_match_image(m[0], m[1], f"@{ref}", f"ROUND OF {tourney.stage}")
            sent_msg = bot.send_photo(TOURNAMENT_CHANNEL, match_img, caption=match_txt)
            if i == 0: tourney.draw_msg_id = sent_msg.message_id

@bot.message_handler(func=lambda m: m.chat.type == 'private' and "WIN" in m.text.upper())
def handle_win(message):
    lines = message.text.split('\n')
    if len(lines) < 2: return
    
    winner = re.search(r"([A-Z0-9]{2,8})", lines[0].upper().replace("WIN", "").strip())
    
    if winner:
        win_name = winner.group(1)
        is_ref = False
        match_idx = -1
        for i, m in enumerate(tourney.matches):
            if win_name in [c.upper() for c in m] and tourney.ref_assignments.get(i+1) == message.from_user.username:
                is_ref = True
                match_idx = i
                break
        
        if is_ref and win_name not in tourney.winners:
            tourney.winners.append(win_name)
            bot.reply_to(message, "✅ تم توثيق النتيجة.")
            
            if tourney.stage == 2:
                final_ref = tourney.ref_assignments.get(match_idx + 1, "None")
                winner_text = f"🏆 نبارك لكلان ⦉ {win_name} ⦊ التتويج!\nالبطل المستحق: 👑 {win_name} 👑\nREFEREE: @{final_ref}"
                bot.send_message(TOURNAMENT_CHANNEL, winner_text)
                tourney.active = False
            else:
                bot.send_message(TOURNAMENT_CHANNEL, f"🏆 فوز الكلان: ⦉ {win_name} ⦊ وتأهله للدور القادم.")
                if len(tourney.winners) == len(tourney.matches): advance()

def advance():
    tourney.clans = list(tourney.winners)
    tourney.stage = len(tourney.clans)
    tourney.winners, tourney.ref_assignments, tourney.klisha_sent = [], {}, False
    bot.send_message(REF_GROUP_ID, f"🔄 جاري الانتقال لدور {tourney.stage} وتوليد القرعة...")
    start_draw_phase()

print("🚀 البوت المنظم يعمل الآن...")
bot.polling(none_stop=True)
