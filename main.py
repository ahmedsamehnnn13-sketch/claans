import telebot
import random
import re
import time
import io
from PIL import Image, ImageDraw, ImageFont

# --- الإعدادات الأساسية ---
TOKEN = '8256105127:AAGRs0n6bGNJ74jXttJnh2Se0AnaW8kworQ'
OWNER_USERNAME = 'levil_8'
PHOTO_URL = "https://i.ibb.co/Vp8pX0D/1000015262.jpg" 
REF_GROUP_ID = -1003875646314      

bot = telebot.TeleBot(TOKEN)

# كلاس البيانات لدعم البطولات المتعددة
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
        self.photo_id = None

# قاموس لتخزين كل بطولة بناءً على معرف القناة
# { channel_id: Tournament_Object }
active_tournaments = {}

# --- دالة توليد تصميم صورة المواجهة ---
def create_match_image(c1, c2, ref, stage_name):
    img = Image.new('RGB', (800, 450), color=(15, 15, 15))
    draw = ImageDraw.Draw(img)
    draw.rectangle([10, 10, 790, 440], outline=(212, 175, 55), width=4)
    draw.rectangle([20, 20, 780, 430], outline=(192, 192, 192), width=1)
    try:
        draw.text((400, 60), f"TOURNEY: {stage_name}", fill=(255, 255, 255), anchor="mm")
        draw.text((200, 225), c1, fill=(255, 255, 255), anchor="mm")
        draw.text((400, 225), "VS", fill=(212, 175, 55), anchor="mm")
        draw.text((600, 225), c2, fill=(255, 255, 255), anchor="mm")
        draw.text((400, 380), f"REFEREE: {ref}", fill=(0, 200, 255), anchor="mm")
    except: pass
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

# --- أوامر التحكم ---
@bot.message_handler(func=lambda m: m.chat.type == 'private' and "بطوله" in m.text)
def start_tour(message):
    if message.from_user.username and message.from_user.username.lower() != OWNER_USERNAME.lower(): return
    
    # استخراج معرف القناة من الرسالة (مثال: بطوله @botolaaatt)
    parts = message.text.split()
    channel_id = parts[1] if len(parts) > 1 else "@botolaaatt"
    
    tour = Tournament(channel_id)
    active_tournaments[channel_id] = tour
    tour.active, tour.stage = True, 16
    
    try:
        msg = bot.send_photo(channel_id, PHOTO_URL, caption=get_reg_text(tour))
        tour.registration_msg_id = msg.message_id
        bot.reply_to(message, f"✅ تم تفعيل بطولة جديدة في القناة {channel_id}")
    except Exception as e:
        bot.reply_to(message, f"❌ فشل الإرسال للقناة {channel_id}. تأكد أن البوت مشرف.\nالخطأ: {e}")

# --- استقبال الكلانات ---
@bot.message_handler(func=lambda m: any(t.active and t.stage == 16 for t in active_tournaments.values()))
def register(message):
    # تحديد أي بطولة ينتمي لها هذا الجروب/القناة
    target_tour = None
    for t in active_tournaments.values():
        if str(t.channel_id) == f"@{message.chat.username}" or str(t.channel_id) == str(message.chat.id):
            target_tour = t
            break
    
    if not target_tour or len(target_tour.clans) >= 16 or message.text.startswith('/'): return
    
    name = message.text.strip().upper()
    if re.match(r"^[A-Z0-9]{2,8}$", name) and name not in target_tour.clans:
        target_tour.clans.append(name)
        try:
            bot.edit_message_caption(get_reg_text(target_tour), target_tour.channel_id, target_tour.registration_msg_id)
        except: pass
        if len(target_tour.clans) == 16: start_draw_phase(target_tour)

# --- القرعة ---
def start_draw_phase(tour):
    random.shuffle(tour.clans)
    tour.matches = [[tour.clans[i], tour.clans[i+1]] for i in range(0, 16, 2)]
    stage_name = "FINAL" if tour.stage == 2 else f"ROUND OF {tour.stage}"
    bot.send_message(REF_GROUP_ID, f"📊 **قرعة {stage_name} لـ {tour.channel_id}**\nحجز بالرد على الرقم:")
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
        # البحث عن البطولة التي تحتاج حجز
        for tour in active_tournaments.values():
            if tour.active and num in range(1, len(tour.matches) + 1) and num not in tour.ref_assignments:
                tour.ref_assignments[num] = message.from_user.username
                bot.reply_to(message, f"✅ حجزت {num} في {tour.channel_id}")
                if len(tour.ref_assignments) == len(tour.matches) and not tour.klisha_sent:
                    tour.klisha_sent = True
                    post_final_draw(tour)
                break
    except: pass

def post_final_draw(tour):
    if tour.stage == 2:
        c1, c2 = tour.matches[0][0], tour.matches[0][1]
        ref = tour.ref_assignments.get(1, "None")
        match_img = create_match_image(c1, c2, f"@{ref}", "GRAND FINAL")
        bot.send_photo(tour.channel_id, match_img, caption=f"⭐️ النهائي المرتقب!\n{c1} VS {c2}\nREFEREE: @{ref}")
    else:
        for i, m in enumerate(tour.matches):
            ref = tour.ref_assignments.get(i+1, "None")
            match_img = create_match_image(m[0], m[1], f"@{ref}", f"ROUND OF {tour.stage}")
            bot.send_photo(tour.channel_id, match_img, caption=f"⦃ {m[0]} ⦄ vs ⦃ {m[1]} ⦄\n𝗥𝗘𝗙: @{ref}")

# --- معالجة الفوز والنتائج ---
@bot.message_handler(func=lambda m: m.chat.type == 'private' and "WIN" in m.text.upper())
def handle_win(message):
    winner_match = re.search(r"([A-Z0-9]{2,8})", message.text.upper().replace("WIN", "").strip())
    if not winner_match: return
    win_name = winner_match.group(1)

    for tour in active_tournaments.values():
        for i, m in enumerate(tour.matches):
            if win_name in [c.upper() for c in m] and tour.ref_assignments.get(i+1) == message.from_user.username:
                if win_name not in tour.winners:
                    # استخراج اسم الخصم المغلوب
                    loser_name = m[0] if m[1].upper() == win_name else m[1]
                    tour.winners.append(win_name)
                    
                    # رابط المنشور (اختياري: يمكن تحسينه لجلب رابط الرسالة الفعلي)
                    post_link = f"https://t.me/{str(tour.channel_id).replace('@','')}/{tour.registration_msg_id}"
                    
                    # صيغة الإعلان المطلوبة
                    win_msg = f"🏆 فوز كلان ⦉ {win_name} ⦊ على كلان ⦉ {loser_name} ⦊ وتأهله للدور القادم.\n\n🔗 رابط البطولة: {post_link}"
                    
                    if tour.stage == 2:
                        bot.send_message(tour.channel_id, f"👑 نبارك لكلان {win_name} فوزه بالبطولة على {loser_name}!")
                    else:
                        bot.send_message(tour.channel_id, win_msg)
                    
                    if len(tour.winners) == len(tour.matches): advance(tour)
                    return

def advance(tour):
    tour.clans = list(tour.winners)
    tour.stage = len(tour.clans)
    tour.winners, tour.ref_assignments, tour.klisha_sent = [], {}, False
    bot.send_message(REF_GROUP_ID, f"🔄 انتقال لدور {tour.stage} في {tour.channel_id}...")
    start_draw_phase(tour)

print("🚀 البوت يعمل بنظام البطولات المتعددة...")
bot.polling(none_stop=True)
