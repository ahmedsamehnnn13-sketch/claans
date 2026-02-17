Import telebot
import random
import re
import time
import io
from PIL import Image, ImageDraw, ImageFont

# --- الإعدادات الأساسية ---
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
        self.klisha_sent = False
        self.photo_id = None

tourney = Tournament()

# --- دالة توليد صورة تجمع كل المواجهات ---
def create_all_matches_image(matches, refs, stage_name):
    # إنشاء خلفية طويلة لتكفي كل المواجهات (عرض 800، طول متغير)
    height = 150 + (len(matches) * 100)
    img = Image.new('RGB', (800, height), color=(15, 15, 15))
    draw = ImageDraw.Draw(img)
    
    # إطار ذهبي خارجي
    draw.rectangle([10, 10, 790, height-10], outline=(212, 175, 55), width=5)
    
    try:
        # العنوان
        draw.text((400, 60), f"TOURNAMENT: {stage_name}", fill=(255, 255, 255), anchor="mm")
        draw.line([200, 90, 600, 90], fill=(212, 175, 55), width=2)
        
        y_offset = 150
        for i, m in enumerate(matches):
            ref_name = refs.get(i+1, "TBA")
            # رسم مستطيل خفيف لكل مواجهة
            draw.rectangle([50, y_offset-40, 750, y_offset+40], outline=(50, 50, 50), width=1)
            
            # نص المواجهة
            match_txt = f"{m[0]}   VS   {m[1]}"
            draw.text((400, y_offset-10), match_txt, fill=(255, 255, 255), anchor="mm")
            # نص الحكم
            draw.text((400, y_offset+15), f"REF: @{ref_name}", fill=(0, 200, 255), anchor="mm")
            
            y_offset += 100
    except:
        pass

    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img_byte_arr

def safe_send(chat_id, caption, custom_photo=None):
    try:
        if custom_photo:
            return bot.send_photo(chat_id, custom_photo, caption=caption)
        return bot.send_photo(chat_id, PHOTO_URL, caption=caption)
    except:
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

@bot.message_handler(func=lambda m: m.chat.type == 'private' and "بطوله" in m.text)
def start_tour(message):
    if message.from_user.username and message.from_user.username.lower() != OWNER_USERNAME.lower(): return
    tourney.active, tourney.stage, tourney.clans = True, 16, []
    tourney.winners, tourney.ref_assignments, tourney.klisha_sent = [], {}, False
    msg = safe_send(TOURNAMENT_CHANNEL, get_reg_text())
    tourney.registration_msg_id = msg.message_id
    bot.reply_to(message, "✅ تم التفعيل. استقبل الكلانات الآن.")

@bot.message_handler(func=lambda m: tourney.active and tourney.stage == 16 and len(tourney.clans) < 16)
def register(message):
    if message.text.startswith('/') or "بطوله" in message.text: return
    name = message.text.strip().upper()
    if re.match(r"^[A-Z0-9]{2,8}$", name) and name not in tourney.clans:
        tourney.clans.append(name)
        bot.reply_to(message, f"✅ سجلت {name} ({len(tourney.clans)}/16)")
        try: bot.edit_message_caption(get_reg_text(), TOURNAMENT_CHANNEL, tourney.registration_msg_id)
        except: pass
        if len(tourney.clans) == 16: start_draw_phase()

def start_draw_phase():
    random.shuffle(tourney.clans)
    tourney.matches = [[tourney.clans[i], tourney.clans[i+1]] for i in range(0, len(tourney.clans), 2)]
    txt = f"📊 **قرعة دور {tourney.stage}**\nحجز المواجهات بالرد على الرقم:\n"
    for i, m in enumerate(tourney.matches):
        txt += f"{i+1}- {m[0]} vs {m[1]}\n"
    bot.send_message(REF_GROUP_ID, txt)

@bot.message_handler(func=lambda m: m.chat.id == REF_GROUP_ID and m.reply_to_message)
def pick_match(message):
    try:
        num = int(re.search(r'\d+', message.text).group())
        if num in range(1, len(tourney.matches) + 1) and num not in tourney.ref_assignments:
            tourney.ref_assignments[num] = message.from_user.username
            bot.reply_to(message, f"✅ حجزت {num}")
            if len(tourney.ref_assignments) == len(tourney.matches) and not tourney.klisha_sent:
                tourney.klisha_sent = True
                post_final_draw()
    except: pass

def post_final_draw():
    if tourney.stage == 2:
        c1, c2 = tourney.matches[0][0], tourney.matches[0][1]
        ref = tourney.ref_assignments.get(1, "None")
        final_klisha = f"""═══════༺⚔༻═══════

✦ بـسـم الـلـه الـرحمـن الـرحـيـم 

═══════༺⚔༻═══════
• نـهائي بطولة THE STRONGEST CLAN
•    
✧━═☆═━━━━•❖•━━━━═☆═━✧

- 𝑭𝑨𝑰𝑵𝑨𝑳 𝑪𝑼𝑷: 

① 𝑪𝑳𝑨𝑵 ✪ ﴾ {c1} ﴿  ⚔ 𝑪𝑳𝑨𝑵 ✪ ﴾ {c2} ﴿

✠ Referee ⟿ ⟦ @{ref} ⟧

❖━═✧═━━━━━✧═━❖

✦ نهائي مشوار طويل وصعب نصل الأن للخطوة الأخير من سيسجل أسمه بطلا للبطولة الصعبه والنارية...؟ 
✧━═☆═━━━━•❖•━━━━═☆═━✧

 •الـقـوانـيـن: 

1- وقت المواجهة ينتهي بعد 3 أيام من نزول القرعة √
2- المواجهات ❻ 𝘃𝘀 ❻  √

★استعدوا… فالميدان لا يرحم إلا الأقوى ★
✧━═☆═━━━━★━━━━═☆═━✧

𝑻𝑯𝑬 𝑩𝑶𝑺𝑺: البوت المنظم ※"""
        img = create_all_matches_image(tourney.matches, tourney.ref_assignments, "GRAND FINAL")
        bot.send_photo(TOURNAMENT_CHANNEL, img, caption=final_klisha)
    else:
        stage_text = f"🏆 قرعة دور {tourney.stage}:\n\n"
        for i, m in enumerate(tourney.matches):
            stage_text += f"⦃ {m[0]} ⦄ vs ⦃ {m[1]} ⦄ ⇇ @{tourney.ref_assignments[i+1]}\n"
        
        img = create_all_matches_image(tourney.matches, tourney.ref_assignments, f"ROUND OF {tourney.stage}")
        bot.send_photo(TOURNAMENT_CHANNEL, img, caption=stage_text)

@bot.message_handler(func=lambda m: m.chat.type == 'private' and "WIN" in m.text.upper())
def handle_win(message):
    winner = re.search(r"([A-Z0-9]{2,8})", message.text.upper().replace("WIN", ""))
    if winner:
        win_name = winner.group(1)
        # التحقق من أن المرسل هو الحكم المسؤول عن هذا الكلان
        for i, m in enumerate(tourney.matches):
            if win_name in [c.upper() for c in m] and tourney.ref_assignments.get(i+1) == message.from_user.username:
                if win_name not in tourney.winners:
                    tourney.winners.append(win_name)
                    bot.reply_to(message, "✅ تم تسجيل الفوز.")
                    if len(tourney.winners) == len(tourney.matches): advance()
                break

def advance():
    tourney.clans = list(tourney.winners)
    tourney.stage = len(tourney.clans)
    tourney.winners, tourney.ref_assignments, tourney.klisha_sent = [], {}, False
    if tourney.stage >= 2:
        bot.send_message(REF_GROUP_ID, f"🔄 تأهل الكلانات لدور {tourney.stage}. جاري القرعة...")
        start_draw_phase()

bot.polling(none_stop=True)
شوف بيعمل ايه. 
خليه يجمعهم كلهم في بتاع واحد بالقرعه بوقت القوايم ب 6/6 في واحده وصوره واحده جمعه كل المواجهات
الحكم يقدر ياخد مواجهتين في دور 16
وواحده بس في 8/4/2 
وخليه لو اتعمل اكتر من بطوله يركز فيهم كلهم مش يسيبهم 
دا البوت الجديد
8256105127:AAGRs0n6bGNJ74jXttJnh2Se0AnaW8kworQ
