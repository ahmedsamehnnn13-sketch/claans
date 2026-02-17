import telebot
import random
import re
import time
import io
from PIL import Image, ImageDraw, ImageFont

# --- الإعدادات الأساسية ---
TOKEN = '8256105127:AAGRs0n6bGNJ74jXttJnh2Se0AnaW8kworQ'
OWNER_USERNAME = 'levil_8'
REF_GROUP_ID = -1003875646314      

bot = telebot.TeleBot(TOKEN)

# قائمة الكلانات الأساسية (تسجيل مسبق)
PRE_REGISTERED_CLANS = ["JUV", "TIT", "SP", "SHR", "JWA", "TDL", "TK", "STO"]

class Tournament:
    def __init__(self, channel_id):
        self.channel_id = channel_id
        self.active = False
        self.stage = 16
        self.clans = list(PRE_REGISTERED_CLANS)
        self.matches = []
        self.ref_assignments = {} 
        self.winners = []
        self.registration_msg_id = None
        self.draw_msg_id = None 
        self.klisha_sent = False

active_tournaments = {}
last_active_channel = None # لمتابعة القناة التي يتم التسجيل لها حالياً

# --- دالة توليد صورة مجمعة احترافية ---
def create_full_tournament_image(matches, refs, stage_name):
    img_height = 250 + (len(matches) * 110)
    img = Image.new('RGB', (800, img_height), color=(10, 10, 10))
    draw = ImageDraw.Draw(img)
    
    draw.rectangle([10, 10, 790, img_height-10], outline=(212, 175, 55), width=6)
    draw.rectangle([20, 20, 780, img_height-20], outline=(40, 40, 40), width=2)
    
    try:
        draw.text((400, 70), "THE STRONGEST CLAN", fill=(212, 175, 55), anchor="mm")
        draw.text((400, 120), f"PHASE: {stage_name}", fill=(255, 255, 255), anchor="mm")
        draw.line([250, 145, 550, 145], fill=(212, 175, 55), width=3)
        
        y_pos = 220
        for i, m in enumerate(matches):
            ref_name = refs.get(i+1, "TBA")
            draw.rectangle([60, y_pos-45, 740, y_pos+45], fill=(20, 20, 20), outline=(60, 60, 60), width=1)
            match_txt = f"{m[0]}   VS   {m[1]}"
            draw.text((400, y_pos-15), match_txt, fill=(255, 255, 255), anchor="mm")
            draw.text((400, y_pos+20), f"REFEREE: @{ref_name}", fill=(0, 200, 255), anchor="mm")
            y_pos += 110
            
        draw.text((400, img_height-60), "SYSTEM: 6 VS 6 | DEADLINE: 3 DAYS", fill=(180, 180, 180), anchor="mm")
    except: pass
    
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img_byte_arr

def create_reg_cover():
    img = Image.new('RGB', (800, 400), color=(15, 15, 15))
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, 800, 400], outline=(212, 175, 55), width=12)
    draw.text((400, 180), "THE STRONGEST CLAN\nTOURNAMENT REGISTRATION", fill=(255, 255, 255), anchor="mm", align="center")
    draw.text((400, 280), f"PRE-REGISTERED: {len(PRE_REGISTERED_CLANS)} | SLOTS LEFT: {16-len(PRE_REGISTERED_CLANS)}", fill=(212, 175, 55), anchor="mm")
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img_byte_arr

def get_reg_text(tour):
    slots = [" "] * 16
    for i in range(len(tour.clans)):
        if i < 16: slots[i] = tour.clans[i]
    icons = ["①","②","③","④","⑤","⑥","⑦","⑧","⑨","①⓪","①①","①②","①③","①④","①⑤","①⑥"]
    list_txt = "".join([f"    {icons[i]}❘➠ 𝗰𝗹𝗮𝗻 ⦉ {slots[i]} ⦊\n" for i in range(16)])
    return f"""- اسعد الله اوقاتكم بكل خير... مُتابعين قنوات الاتحاد العربي.
━─── ••◦⊱≼≽⊰◦•• ───━
الـيـكـم بطوله ⦉ THE STRONGEST CLAN ⦊
{list_txt}
تنظيم ⤇⦇ البوت المنظم ⦈
اشراف⤇⦇ الـلـجـنـة الـعـل -يـا ⦈"""

@bot.message_handler(func=lambda m: m.chat.type == 'private' and "بطوله" in m.text)
def start_tour(message):
    global last_active_channel
    if message.from_user.username and message.from_user.username.lower() != OWNER_USERNAME.lower(): return
    parts = message.text.split()
    channel_id = parts[1] if len(parts) > 1 else "@botolaaatt"
    if not channel_id.startswith('@') and not str(channel_id).startswith('-100'): channel_id = f"@{channel_id}"

    tour = Tournament(channel_id)
    active_tournaments[channel_id] = tour
    tour.active, tour.stage = True, 16
    last_active_channel = channel_id # تحديد هذه القناة كوجهة للتسجيل حالياً
    
    try:
        cover = create_reg_cover()
        msg = bot.send_photo(channel_id, cover, caption=get_reg_text(tour))
        tour.registration_msg_id = msg.message_id
        bot.reply_to(message, f"✅ تم تفعيل البطولة في {channel_id}\n(تم تسجيل 8 كلانات أساسية تلقائياً)")
    except Exception as e:
        bot.reply_to(message, f"❌ فشل الإرسال: {e}")

# --- تعديل دالة التسجيل لتعمل في الخاص أو المجموعات ---
@bot.message_handler(func=lambda m: last_active_channel is not None and len(active_tournaments[last_active_channel].clans) < 16)
def register(message):
    global last_active_channel
    tour = active_tournaments.get(last_active_channel)
    
    if not tour or not tour.active or tour.stage != 16 or message.text.startswith('/'): return
    
    name = message.text.strip().upper()
    # التحقق من شروط اسم الكلان (حروف وأرقام من 2 لـ 8)
    if re.match(r"^[A-Z0-9]{2,8}$", name) and name not in tour.clans:
        tour.clans.append(name)
        try: 
            bot.edit_message_caption(get_reg_text(tour), tour.channel_id, tour.registration_msg_id)
            bot.reply_to(message, f"✅ تم تسجيل كلان {name} بنجاح في القائمة.")
        except: pass
        
        if len(tour.clans) == 16: 
            start_draw_phase(tour)

def start_draw_phase(tour):
    random.shuffle(tour.clans)
    tour.matches = [[tour.clans[i], tour.clans[i+1]] for i in range(0, 16, 2)]
    stage_name = "FINAL" if tour.stage == 2 else f"ROUND OF {tour.stage}"
    bot.send_message(REF_GROUP_ID, f"📊 **قرعة {stage_name} للقناة {tour.channel_id}**\nيرجى حجز المواجهات بالرد على الرقم:")
    send_ref_list(tour)

def send_ref_list(tour):
    txt = f"مواجهات {tour.stage} ({tour.channel_id}):\n"
    for i, m in enumerate(tour.matches):
        ref = tour.ref_assignments.get(i+1, "متاح ✅")
        txt += f"{i+1}- {m[0]} vs {m[1]} ⇇ {ref if ref == 'متاح ✅' else '@'+ref}\n"
    bot.send_message(REF_GROUP_ID, txt)

@bot.message_handler(func=lambda m: m.chat.id == REF_GROUP_ID and m.reply_to_message)
def pick_match(message):
    try:
        num = int(re.search(r'\d+', message.text).group())
        for tour in active_tournaments.values():
            if tour.active and num in range(1, len(tour.matches) + 1) and num not in tour.ref_assignments:
                tour.ref_assignments[num] = message.from_user.username
                bot.reply_to(message, f"✅ تم الحجز {num} في {tour.channel_id}")
                if len(tour.ref_assignments) == len(tour.matches) and not tour.klisha_sent:
                    tour.klisha_sent = True
                    post_final_draw(tour)
                break
    except: pass

def post_final_draw(tour):
    stage_name = "GRAND FINAL" if tour.stage == 2 else f"ROUND OF {tour.stage}"
    full_img = create_full_tournament_image(tour.matches, tour.ref_assignments, stage_name)
    
    combined_msg = f"═══════༺⚔༻═══════\n✦ قرعة دور {tour.stage} مجمعة\n═══════༺⚔༻═══════\n"
    for i, m in enumerate(tour.matches):
        combined_msg += f"● {m[0]} 🆚 {m[1]} ➟ @{tour.ref_assignments.get(i+1)}\n"
    
    combined_msg += f"\n• الـنـظـام: 6 𝘃𝘀 6\n• الـقـوانـيـن: مـمـنـوع الـغـدر | الـتـزام بالـوقت\n• الـمـدة: 3 أيام\n• الـتـنـظـيـم: الـبـوت الـمـنـظـم ※\n✧━═☆═━━━━━★━━━━━═☆═━✧"
    
    bot.send_photo(tour.channel_id, full_img, caption=combined_msg)

@bot.message_handler(func=lambda m: m.chat.type == 'private' and "WIN" in m.text.upper())
def handle_win(message):
    winner_match = re.search(r"([A-Z0-9]{2,8})", message.text.upper().replace("WIN", "").strip())
    if not winner_match: return
    win_name = winner_match.group(1)

    for tour in active_tournaments.values():
        for i, m in enumerate(tour.matches):
            if win_name in [c.upper() for c in m] and tour.ref_assignments.get(i+1) == message.from_user.username:
                if win_name not in tour.winners:
                    loser_name = m[0] if m[1].upper() == win_name else m[1]
                    tour.winners.append(win_name)
                    channel_clean = str(tour.channel_id).replace('@', '')
                    post_link = f"https://t.me/{channel_clean}/{tour.registration_msg_id}"
                    
                    final_msg = f"🏆 فوز كلان ⦉ {win_name} ⦊ على كلان ⦉ {loser_name} ⦊ وتأهله للدور القادم.\n\n🔗 رابط البطولة: {post_link}"
                    bot.send_message(tour.channel_id, final_msg)
                    if len(tour.winners) == len(tour.matches): advance(tour)
                    return

def advance(tour):
    tour.clans = list(tour.winners)
    tour.stage = len(tour.clans)
    tour.winners, tour.ref_assignments, tour.klisha_sent = [], {}, False
    bot.send_message(REF_GROUP_ID, f"🔄 تأهل الكلانات لدور {tour.stage} في {tour.channel_id}. جاري توليد القرعة...")
    start_draw_phase(tour)

print("🚀 البوت يعمل الآن... التسجيل متاح في الخاص للبوت.")
bot.polling(none_stop=True)
