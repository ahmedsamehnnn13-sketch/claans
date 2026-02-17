import telebot
import random
import re
import time
import io
from PIL import Image, ImageDraw, ImageFont

# --- الإعدادات الأساسية ---
TOKEN = '8256105127:AAGRs0n6bGNJ74jXttJnh2Se0AnaW8kworQ'
OWNER_USERNAME = 'levil_8'
# تم الاستغناء عن PHOTO_URL الخارجي لتجنب أخطاء الـ Bad Request
REF_GROUP_ID = -1003875646314      

bot = telebot.TeleBot(TOKEN)

class Tournament:
    def __init__(self, channel_id):
        self.channel_id = channel_id
        self.active = False
        self.stage = 16
        self.clans = []
        self.matches = []
        self.ref_assignments = {} 
        self.winners = []
        self.registration_msg_id = None
        self.draw_msg_id = None 
        self.klisha_sent = False

active_tournaments = {}

# --- دالة توليد صورة مجمعة لكل المواجهات ---
def create_full_tournament_image(matches, refs, stage_name):
    # حساب الطول بناءً على عدد المباريات
    img_height = 200 + (len(matches) * 100)
    img = Image.new('RGB', (800, img_height), color=(15, 15, 15))
    draw = ImageDraw.Draw(img)
    
    # إطارات ذهبية
    draw.rectangle([10, 10, 790, img_height-10], outline=(212, 175, 55), width=5)
    
    try:
        # العنوان
        draw.text((400, 60), f"TOURNAMENT: {stage_name}", fill=(255, 255, 255), anchor="mm")
        draw.line([200, 90, 600, 90], fill=(212, 175, 55), width=2)
        
        y_pos = 160
        for i, m in enumerate(matches):
            ref_name = refs.get(i+1, "TBA")
            # رسم مستطيل خفيف للمواجهة
            draw.rectangle([50, y_pos-40, 750, y_pos+40], outline=(50, 50, 50), width=1)
            match_txt = f"{m[0]}   VS   {m[1]}"
            draw.text((400, y_pos-10), match_txt, fill=(255, 255, 255), anchor="mm")
            draw.text((400, y_pos+20), f"REF: @{ref_name}", fill=(0, 200, 255), anchor="mm")
            y_pos += 100
            
        draw.text((400, img_height-50), "SYSTEM: 6 VS 6 | TIME: 3 DAYS", fill=(150, 150, 150), anchor="mm")
    except: pass
    
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img_byte_arr

# دالة إنشاء صورة غلاف التسجيل (بديلة للرابط المتعطل)
def create_reg_cover():
    img = Image.new('RGB', (800, 400), color=(20, 20, 20))
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, 800, 400], outline=(212, 175, 55), width=10)
    draw.text((400, 200), "THE STRONGEST CLAN\nREGISTRATION START", fill=(255, 255, 255), anchor="mm", align="center")
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
اشراف⤇⦇ الـلـجـنـة الـعـلـيـا ⦈"""

@bot.message_handler(func=lambda m: m.chat.type == 'private' and "بطوله" in m.text)
def start_tour(message):
    if message.from_user.username and message.from_user.username.lower() != OWNER_USERNAME.lower(): return
    parts = message.text.split()
    channel_id = parts[1] if len(parts) > 1 else "@botolaaatt"
    if not channel_id.startswith('@') and not str(channel_id).startswith('-100'): channel_id = f"@{channel_id}"

    tour = Tournament(channel_id)
    active_tournaments[channel_id] = tour
    tour.active, tour.stage = True, 16
    
    try:
        cover = create_reg_cover()
        msg = bot.send_photo(channel_id, cover, caption=get_reg_text(tour))
        tour.registration_msg_id = msg.message_id
        bot.reply_to(message, f"✅ تم تفعيل البطولة في {channel_id}")
    except Exception as e:
        bot.reply_to(message, f"❌ فشل الإرسال للقناة {channel_id}: {e}")

@bot.message_handler(func=lambda m: any(t.active and t.stage == 16 for t in active_tournaments.values()))
def register(message):
    current_chat = f"@{message.chat.username}" if message.chat.username else str(message.chat.id)
    tour = active_tournaments.get(current_chat)
    if not tour or len(tour.clans) >= 16 or message.text.startswith('/'): return
    
    name = message.text.strip().upper()
    if re.match(r"^[A-Z0-9]{2,8}$", name) and name not in tour.clans:
        tour.clans.append(name)
        try: bot.edit_message_caption(get_reg_text(tour), tour.channel_id, tour.registration_msg_id)
        except: pass
        if len(tour.clans) == 16: start_draw_phase(tour)

def start_draw_phase(tour):
    random.shuffle(tour.clans)
    tour.matches = [[tour.clans[i], tour.clans[i+1]] for i in range(0, 16, 2)]
    stage_name = "FINAL" if tour.stage == 2 else f"ROUND OF {tour.stage}"
    bot.send_message(REF_GROUP_ID, f"📊 **قرعة {stage_name} للقناة {tour.channel_id}**\nحجز بالرد على الرقم:")
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
    # إنشاء الصورة المجمعة
    stage_name = "GRAND FINAL" if tour.stage == 2 else f"ROUND OF {tour.stage}"
    full_img = create_full_tournament_image(tour.matches, tour.ref_assignments, stage_name)
    
    # الكليشة المجمعة
    combined_msg = f"═══════༺⚔༻═══════\n✦ قرعة دور {tour.stage} مجمعة\n═══════༺⚔༻═══════\n"
    for i, m in enumerate(tour.matches):
        combined_msg += f"● {m[0]} 🆚 {m[1]} ➟ @{tour.ref_assignments.get(i+1)}\n"
    
    combined_msg += f"\n• الـنـظـام: 6 𝘃𝘀 6\n• الـمـدة: 3 أيام\n• الـتـنـظـيـم: الـبـوت الـمـنـظـم ※\n✧━═☆═━━━━━★━━━━━═☆═━✧"
    
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
    bot.send_message(REF_GROUP_ID, f"🔄 تأهل الكلانات لدور {tour.stage} في {tour.channel_id}...")
    start_draw_phase(tour)

print("🚀 البوت المطور يعمل الآن...")
bot.polling(none_stop=True)
