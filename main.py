import telebot
import random
import re
import time

# --- الإعدادات الأساسية المعدلة ---
TOKEN = '8113358654:AAF6crTuiDikhfQz56twot-1vGs7exwdaTQ'
OWNER_USERNAME = 'levil_8'
TOURNAMENT_CHANNEL = "@botolaaatt"  # القناة الجديدة
REF_GROUP_ID = -1003875646314      # جروب الحكام الجديد
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

# دالة إرسال الصورة أو نص عند الفشل
def safe_send(chat_id, caption):
    try:
        if tourney.photo_id:
            return bot.send_photo(chat_id, tourney.photo_id, caption=caption)
        else:
            msg = bot.send_photo(chat_id, PHOTO_URL, caption=caption)
            tourney.photo_id = msg.photo[-1].file_id
            return msg
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

# --- أوامر التحكم ---
@bot.message_handler(func=lambda m: m.chat.type == 'private' and "بطوله" in m.text)
def start_tour(message):
    if message.from_user.username and message.from_user.username.lower() != OWNER_USERNAME.lower():
        return
    
    tourney.active, tourney.stage, tourney.clans = True, 16, []
    tourney.winners, tourney.ref_assignments, tourney.klisha_sent = [], {}, False
    
    msg = safe_send(TOURNAMENT_CHANNEL, get_reg_text())
    tourney.registration_msg_id = msg.message_id
    bot.reply_to(message, "✅ بدأت البطولة! تم النشر في القناة، بانتظار تسجيل 16 كلان.")

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
    
    if tourney.stage == 2:
        bot.send_message(REF_GROUP_ID, f"🏆 **وصلنا للنهائي المرتقب!**\n{tourney.matches[0][0]} 🆚 {tourney.matches[0][1]}\nيرجى من الحكم حجز المباراة بالرد برقم 1.")
    else:
        bot.send_message(REF_GROUP_ID, f"📊 **قرعة دور {tourney.stage} جاهزة!**\nيرجى من الحكام الرد برقم المواجهة لحجزها:")
    
    send_ref_list()

def send_ref_list():
    txt = f"قائمة مواجهات دور {tourney.stage}:\n"
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
            bot.reply_to(message, f"✅ تم حجزك للمواجهة {num}")
            
            if len(tourney.ref_assignments) == len(tourney.matches) and not tourney.klisha_sent:
                tourney.klisha_sent = True
                post_final_draw()
    except: pass

def post_final_draw():
    if tourney.stage == 2:
        # كليشة النهائي المرتقب في القناة
        c1, c2 = tourney.matches[0][0], tourney.matches[0][1]
        ref = tourney.ref_assignments.get(1, "Unknown")
        txt = f"""⭐️الان وصلنا وأياكم الى قمة النهائي المرتقب الذي يجمع مـا بين كلان {c2} و {c1}
من سيخطف لقب النسخة اولى ؟ 

وهي البـطوله العريقة جداً

🔤🤩 THE STRONGEST CLAN - 1 🤩🔤

علمًا أن النهائي تم تأجيله لفتره وتم افتتاح النهائي لِنسخه ثانيه وكان البطل بانتظار الحسم..
  
           .     📍 {c2} 🆚 {c1} 📍      .

REFEREE 👾 @{ref}
➖➖➖➖➖➖➖➖➖➖
➖➖➖➖➖➖➖➖➖➖
- المنـظم 👾 بـوت الـمـنـظـمـيـن 🤍.
- المشرف 👾 اللجنه العليا  ❤️‍🔥.."""
    else:
        # حساب وقت القوائم بناءً على الدور
        list_time = 14 if tourney.stage in [16, 8] else 18
        
        blocks = ""
        for i, m in enumerate(tourney.matches):
            ref = tourney.ref_assignments.get(i+1, "None")
            blocks += f"""{i+1} ➸ {m[0]} 🆚 {m[1]} 
الحكم ➜ @{ref} ⚐ . 
━─── ••◦⊱≼≽⊰◦•• ───━\n"""

        txt = f"""- اسعد الله اوقاتكم بكل خير اينما كُنتم مُتابعين قنوات الاتحاد العربي للكلانات .
━─── ••◦⊱≼≽⊰◦•• ───━
الـيـكـم قـرعة دور الـ {tourney.stage} مـن بـطـولـه :
《 𝗹𝗶𝗼𝗻 𝗼𝗳 𝘁𝗵𝗲 𝗷𝘂𝗻𝗴𝗹𝗲  》
━─── ••◦⊱≼≽⊰◦•• ───━
{blocks}
               ⦕   الـقـوانـيـن  ⦖

➀ ➝ المواجهات ❻ VS ❻.
➁ ➝ أخر وقت لقوائم بعد {list_time} ساعة .
➂ ➝ تراسل الحكم مو تنتظرة يراسلك
➃ ➝ وقت المواجهة يومين ⌛️."""

    msg = safe_send(TOURNAMENT_CHANNEL, txt)
    tourney.draw_msg_id = msg.message_id

@bot.message_handler(func=lambda m: m.chat.type == 'private' and "WIN" in m.text.upper())
def handle_win(message):
    lines = message.text.split('\n')
    if len(lines) < 2: return
    
    winner = re.search(r"([A-Z0-9]{2,8})", lines[0].upper().replace("WIN", "").strip())
    link = re.search(r"/(\d+)$", lines[1])
    
    if winner and link:
        win_name = winner.group(1)
        if int(link.group(1)) != tourney.draw_msg_id: return
        
        is_ref = False
        match_idx = -1
        for i, m in enumerate(tourney.matches):
            if win_name in [c.upper() for c in m] and tourney.ref_assignments.get(i+1) == message.from_user.username:
                is_ref = True
                match_idx = i
                break
        
        if is_ref and win_name not in tourney.winners:
            tourney.winners.append(win_name)
            bot.reply_to(message, "✅ تم تسجيل الفوز بنجاح.")
            
            # إذا كان النهائي
            if tourney.stage == 2:
                final_ref = tourney.ref_assignments.get(match_idx + 1, "Unknown")
                c1, c2 = tourney.matches[0][0], tourney.matches[0][1]
                winner_text = f"""🏆 نبارك لكلان ⦉ {win_name} ⦊ تتويجه بلقب البطولة!

⭐️ نهاية النهائي المرتقب مـا بين كلان {c2} و {c1}

🔤🤩 THE STRONGEST CLAN - 1 🤩🔤

البطل المستحق: 👑 {win_name} 👑

REFEREE 👾 @{final_ref}
➖➖➖➖➖➖➖➖➖➖
➖➖➖➖➖➖➖➖➖➖
- المنـظم 👾 بـوت الـمـنـظـمـيـن 🤍.
- المشرف 👾 اللجنه العليا  ❤️‍🔥.."""
                safe_send(TOURNAMENT_CHANNEL, winner_text)
                tourney.active = False
            else:
                bot.send_message(TOURNAMENT_CHANNEL, f"🏆 فوز الكلان: ⦉ {win_name} ⦊\nمبروك التأهل لدور {tourney.stage // 2}!")
                if len(tourney.winners) == len(tourney.matches):
                    advance()

def advance():
    tourney.clans = list(tourney.winners)
    tourney.stage = len(tourney.clans)
    tourney.winners, tourney.ref_assignments, tourney.klisha_sent = [], {}, False
    bot.send_message(REF_GROUP_ID, f"🚀 اكتملت نتائج الدور الحالي. جاري الانتقال لدور {tourney.stage}...")
    start_draw_phase()

bot.polling(none_stop=True)
