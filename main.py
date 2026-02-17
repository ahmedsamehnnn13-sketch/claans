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
PHOTO_URL = "https://i.ibb.co/Vp8pX0D/1000015262.jpg" 
# الرابط الذي طلبته تم تعيينه كمعرف القناة الافتراضي
TOURNAMENT_CHANNEL = '@botolaaatt' 

bot = telebot.TeleBot(TOKEN)

# نظام تخزين البطولات المتعددة لضمان عدم التداخل
class TournamentData:
    def __init__(self, channel_id):
        self.channel_id = channel_id
        self.active = False
        self.stage = 16
        self.clans = []
        self.matches = []
        self.ref_assignments = {} 
        self.winners = []
        self.registration_msg_id = None
        self.klisha_sent = False

# قاموس لتخزين بيانات كل بطولة بناءً على معرف القناة
active_tourneys = {}

# --- دالة توليد صورة تجمع كل المواجهات ---
def create_all_matches_image(matches, refs, stage_name):
    height = 180 + (len(matches) * 110)
    img = Image.new('RGB', (800, height), color=(15, 15, 15))
    draw = ImageDraw.Draw(img)
    
    draw.rectangle([10, 10, 790, height-10], outline=(212, 175, 55), width=5)
    
    try:
        # ملاحظة: إذا لم يتوفر ملف خط محدد، سيستخدم النظام الخط الافتراضي
        draw.text((400, 60), f"TOURNAMENT: {stage_name}", fill=(255, 255, 255), anchor="mm")
        draw.line([200, 90, 600, 90], fill=(212, 175, 55), width=2)
        
        y_offset = 160
        for i, m in enumerate(matches):
            ref_name = refs.get(i+1, "TBA")
            draw.rectangle([50, y_offset-45, 750, y_offset+45], outline=(50, 50, 50), width=1)
            match_txt = f"{m[0]}   VS   {m[1]}"
            draw.text((400, y_offset-12), match_txt, fill=(255, 255, 255), anchor="mm")
            draw.text((400, y_offset+18), f"REF: @{ref_name}", fill=(0, 200, 255), anchor="mm")
            y_offset += 110
    except Exception as e:
        print(f"Draw error: {e}")

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
اشراف⤇⦇ الـلـجـنـة الـعـلـيـا ⦈
رابط القناة ⤇ {TOURNAMENT_CHANNEL}"""

# --- أوامر التحكم ---
@bot.message_handler(func=lambda m: m.chat.type == 'private' and "بطوله" in m.text)
def start_tour(message):
    if message.from_user.username and message.from_user.username.lower() != OWNER_USERNAME.lower(): 
        return
    
    channel_id = TOURNAMENT_CHANNEL
    tour = TournamentData(channel_id)
    active_tourneys[channel_id] = tour
    
    tour.active, tour.stage = True, 16
    try:
        msg = bot.send_photo(channel_id, PHOTO_URL, caption=get_reg_text(tour))
        tour.registration_msg_id = msg.message_id
        bot.reply_to(message, f"✅ تم تفعيل البطولة في {channel_id}.")
    except Exception as e:
        bot.reply_to(message, f"❌ خطأ: تأكد أن البوت مشرف في {channel_id}\nالوصف: {e}")

@bot.message_handler(func=lambda m: m.chat.type in ['channel', 'supergroup', 'group'])
def handle_registration(message):
    # البحث عن البطولة النشطة لهذه القناة أو الجروب
    chat_id = message.chat.username if message.chat.username else message.chat.id
    if isinstance(chat_id, str) and not chat_id.startswith('@'):
        chat_id = '@' + chat_id
        
    tour = active_tourneys.get(chat_id) or active_tourneys.get(message.chat.id)
    
    if tour and tour.active and tour.stage == 16 and len(tour.clans) < 16:
        name = message.text.strip().upper()
        if re.match(r"^[A-Z0-9]{2,8}$", name) and name not in tour.clans:
            tour.clans.append(name)
            if len(tour.clans) == 16: 
                start_draw_phase(tour)
            try: 
                bot.edit_message_caption(get_reg_text(tour), tour.channel_id, tour.registration_msg_id)
            except: 
                pass

def start_draw_phase(tour):
    random.shuffle(tour.clans)
    tour.matches = [[tour.clans[i], tour.clans[i+1]] for i in range(0, len(tour.clans), 2)]
    tour.klisha_sent = False
    tour.ref_assignments = {}
    
    txt = f"📊 **قرعة دور {tour.stage} للقناة {tour.channel_id}**\nحجز المواجهات بالرد على الرقم:\n"
    for i, m in enumerate(tour.matches):
        txt += f"{i+1}- {m[0]} vs {m[1]}\n"
    bot.send_message(REF_GROUP_ID, txt)

@bot.message_handler(func=lambda m: m.chat.id == REF_GROUP_ID and m.reply_to_message)
def pick_match(message):
    try:
        num_match = re.search(r'\d+', message.text)
        if not num_match: return
        num = int(num_match.group())
        ref_user = message.from_user.username
        
        for tour in active_tourneys.values():
            if tour.active and num in range(1, len(tour.matches) + 1) and num not in tour.ref_assignments:
                user_bookings = list(tour.ref_assignments.values()).count(ref_user)
                max_allowed = 2 if tour.stage == 16 else 1
                
                if user_bookings < max_allowed:
                    tour.ref_assignments[num] = ref_user
                    bot.reply_to(message, f"✅ تم حجز المواجهة {num} للحكم @{ref_user}")
                    
                    if len(tour.ref_assignments) == len(tour.matches) and not tour.klisha_sent:
                        tour.klisha_sent = True
                        post_combined_draw(tour)
                else:
                    bot.reply_to(message, f"❌ عذراً، مسموح لك بـ {max_allowed} مواجهة فقط.")
                break
    except: pass

def post_combined_draw(tour):
    if tour.stage == 2:
        c1, c2 = tour.matches[0][0], tour.matches[0][1]
        ref = tour.ref_assignments.get(1, "None")
        final_klisha = f"""═══════༺⚔༻═══════
✦ بـسـم الـلـه الـرحمـن الـرحـيـم 
═══════༺⚔༻═══════
• نـهائي بطولة ⦉ THE STRONGEST CLAN ⦊
✧━═☆═━━━━•❖•━━━━═☆═━✧
- 𝑭𝑨𝑰𝑵𝑨𝑳 𝑪𝑼𝑷: 
① 𝑪𝑳𝑨𝑵 ✪ ﴾ {c1} ﴿  ⚔ 𝑪𝑳𝑨𝑵 ✪ ﴾ {c2} ﴿
✠ Referee ⟿ ⟦ @{ref} ⟧
❖━═✧═━━━━━✧═━❖
✦ نهائي مشوار طويل وصعب...
✧━═☆═━━━━•❖•━━━━═☆═━✧
𝑻𝑯𝑬 𝑩𝑶𝑺𝑺: البوت المنظم ※"""
        img = create_all_matches_image(tour.matches, tour.ref_assignments, "GRAND FINAL")
        bot.send_photo(tour.channel_id, img, caption=final_klisha)
    else:
        combined_text = f"═══════༺⚔༻═══════\n✦ قرعة دور {tour.stage} مجمعة\n═══════༺⚔༻═══════\n"
        for i, m in enumerate(tour.matches):
            combined_text += f"● {m[0]} 🆚 {m[1]} ➟ @{tour.ref_assignments.get(i+1, 'TBA')}\n"
        combined_text += f"\n• القوانين: 6 𝘃𝘀 6\n• مدة الدور: 3 أيام\n𝑻𝑯𝑬 𝑩𝑶𝑺𝑺: البوت المنظم ※"
        
        img = create_all_matches_image(tour.matches, tour.ref_assignments, f"ROUND OF {tour.stage}")
        bot.send_photo(tour.channel_id, img, caption=combined_text)

@bot.message_handler(func=lambda m: m.chat.type == 'private' and "WIN" in m.text.upper())
def handle_win(message):
    winner = re.search(r"([A-Z0-9]{2,8})", message.text.upper().replace("WIN", ""))
    if winner:
        win_name = winner.group(1)
        for tour in active_tourneys.values():
            for i, m in enumerate(tour.matches):
                if win_name in [c.upper() for c in m] and tour.ref_assignments.get(i+1) == message.from_user.username:
                    if win_name not in tour.winners:
                        tour.winners.append(win_name)
                        bot.reply_to(message, f"✅ تم تسجيل فوز {win_name}")
                        if len(tour.winners) == len(tour.matches): 
                            advance(tour)
                    return

def advance(tour):
    tour.clans = list(tour.winners)
    tour.stage = len(tour.clans)
    tour.winners, tour.ref_assignments, tour.klisha_sent = [], {}, False
    if tour.stage >= 2:
        bot.send_message(REF_GROUP_ID, f"🔄 تأهل الكلانات لدور {tour.stage}. جاري القرعة...")
        start_draw_phase(tour)
    else:
        tour.active = False

print("البوت يعمل الآن...")
bot.polling(none_stop=True)
