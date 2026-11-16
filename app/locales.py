"""Uch tilli matnlar. O'zbekchasi @anonAskBot dagi matnlarga moslangan."""
from __future__ import annotations

from typing import Any

from app import emoji_pack

DEFAULT_LANG = "uz"
LANG_NAMES = {"uz": "🇺🇿 O'zbekcha", "ru": "🇷🇺 Русский", "en": "🇬🇧 English"}


def normalize_lang(code: str | None) -> str:
    if not code:
        return DEFAULT_LANG
    code = code.lower()
    if code.startswith("uz"):
        return "uz"
    if code.startswith("ru"):
        return "ru"
    if code.startswith("en"):
        return "en"
    return DEFAULT_LANG


TEXTS: dict[str, dict[str, str]] = {
    # ================================================================ UZ
    "uz": {
        "start_main": (
            "Hoziroq anonim xabarlarni olishni boshlang 🚀\n\n"
            "Sizning havolangiz 👇\n"
            "<blockquote>{link}</blockquote>\n"
            "<b>Ushbu havolani ☝️ 📱/🎵/📷 profil tavsifiga joylashtiring, "
            "shunda anonim xabarlar ola boshlaysiz</b> 💬"
        ),
        "anon_prompt": (
            "🔗 Bu yerda ushbu havolani joylashtirgan kishiga "
            "<b>anonim xabar</b> yuborish mumkin.\n\n"
            "💡 <b>Unga yetkazmoqchi bo'lgan barcha narsangizni shu yerga yozing</b>, "
            "va bir necha soniyadan so'ng u xabaringizni oladi, "
            "ammo kimdanligini bilmaydi.\n"
            "<blockquote>Yuborishingiz mumkin: matn, rasm, video, stikerlar, "
            "ovozli va video xabarlar (dumaloq)</blockquote>"
        ),
        "sent_ok": "✅ Xabar yuborildi, javob kuting!",
        "reply_sent": "✅ Javob yuborildi!",
        # kelgan xabarlar
        "incoming_text": (
            "💬 <b>Sizda yangi anonim xabar bor!</b>\n\n"
            "<blockquote>{text}</blockquote>\n\n"
            "↩️ <i>Javob berish uchun suring.</i>"
        ),
        "incoming_media": (
            "💬 <b>Sizda yangi anonim xabar bor!</b>\n\n"
            "↩️ <i>Javob berish uchun suring.</i>"
        ),
        "reply_text": (
            "✉️ <b>Anonim xabaringizga javob keldi!</b>\n\n"
            "<blockquote>{text}</blockquote>\n\n"
            "↩️ <i>Javob berish uchun suring.</i>"
        ),
        "reply_media": (
            "✉️ <b>Anonim xabaringizga javob keldi!</b>\n\n"
            "↩️ <i>Javob berish uchun suring.</i>"
        ),
        # /mystats
        "mystats": (
            "📊 <b>Profil statistikasi</b>\n\n"
            "🔹 <b>Bugun:</b>\n"
            "<blockquote>💬 Xabarlar: {msg_today}\n"
            "👀 Havola orqali o'tishlar: {views_today}\n"
            "👑 Mashhurlik: {pop_today}/10</blockquote>\n\n"
            "🔹 <b>Jami davr mobaynida:</b>\n"
            "<blockquote>💬 Xabarlar: {msg_total}\n"
            "👀 Havola orqali o'tishlar: {views_total}\n"
            "👑 Mashhurlik: {pop_total}/10</blockquote>\n\n"
            "⭐️ <i>Mashhurlik darajasini oshirish uchun "
            "o'z shaxsiy havolangizni tarqating:</i>\n👉 {link}"
        ),
        # /url
        "url_ask": (
            "🔗 <b>Havolani yangilaysizmi?</b>\n\n"
            "Hozirgi havolangiz:\n<blockquote>{link}</blockquote>\n"
            "⚠️ Yangilasangiz <b>eski havola ishlamay qoladi</b> — "
            "uni profilingizda ham almashtirishingiz kerak bo'ladi."
        ),
        "url_changed": (
            "✅ <b>Havolangiz yangilandi!</b>\n\n"
            "<blockquote>{link}</blockquote>\n\n"
            "Eski havola endi ishlamaydi."
        ),
        # /issue
        "issue_prompt": (
            "💡 <b>G'oyangiz yoki muammoni yozing</b> — men uni "
            "bot egasiga yetkazaman.\n\nBekor qilish uchun /start bosing."
        ),
        "issue_sent": "✅ Rahmat! Xabaringiz yetkazildi.",
        "issue_nowhere": "⚠️ Hozircha g'oyalarni qabul qiladigan admin sozlanmagan.",
        # yordam
        "help": (
            "❓ <b>Bot qanday ishlaydi?</b>\n\n"
            "1️⃣ Shaxsiy havolangizni profilingizga joylaysiz.\n"
            "2️⃣ Do'stlaringiz havolani bosib, sizga anonim yozadi.\n"
            "3️⃣ Xabar sizga keladi — kim yozganini bilmaysiz.\n"
            "4️⃣ Javob berish uchun o'sha xabarni <b>surib</b> (reply qilib) "
            "javobingizni yozasiz.\n\n"
            "<b>Buyruqlar:</b>\n"
            "/start — havolani olish\n"
            "/mystats — statistikangiz\n"
            "/url — havolani yangilash\n"
            "/issue — g'oya yoki shikoyat\n"
            "/settings — sozlamalar (til, bloklanganlar)"
        ),
        # xatolar
        "self_not_allowed": "🙃 O'zingizga anonim xabar yozolmaysiz.",
        "user_not_found": "❓ Bunday foydalanuvchi topilmadi. Havola eskirgan bo'lishi mumkin.",
        "not_accepting": "🔕 Bu foydalanuvchi hozircha anonim xabarlarni qabul qilmayapti.",
        "you_are_blocked": "🚫 Bu foydalanuvchi sizni bloklagan, xabar yetib bormaydi.",
        "receiver_unavailable": (
            "⚠️ Xabarni yetkazib bo'lmadi — foydalanuvchi botni to'xtatgan yoki bloklagan."
        ),
        "msg_not_found": "⚠️ Bu xabar topilmadi yoki juda eski.",
        "reply_prompt": "✍️ Javobingizni yozing — u anonim ketadi.",
        "reply_hint": (
            "↩️ Javob berish uchun <b>kelgan xabarni surib</b> (reply qilib) yozing."
        ),
        "unsupported": "⚠️ Bu turdagi xabarni yuborib bo'lmaydi. Boshqasini sinab ko'ring.",
        "flood": "🐢 Juda tez yozyapsiz, bir oz sekinroq.",
        "cancelled": "❌ Bekor qilindi.",
        "nothing_to_cancel": "ℹ️ Hozir bekor qiladigan narsa yo'q.",
        "deleted_ok": "🗑 Xabar o'chirildi.",
        # sozlamalar
        "settings_title": (
            "⚙️ <b>Sozlamalar</b>\n\n"
            "🌐 Til: {lang}\n"
            "🔔 Anonim xabarlar: {accepting}\n"
            "🚫 Bloklanganlar: {blocked}"
        ),
        "on": "yoqilgan ✅",
        "off": "o'chirilgan ❌",
        "lang_choose": "🌐 Tilni tanlang:",
        "lang_set": "✅ Til o'zgartirildi.",
        "accepting_on": "🔔 Endi anonim xabarlar qabul qilinadi.",
        "accepting_off": "🔕 Anonim xabarlar vaqtincha qabul qilinmaydi.",
        "blocked_ok": "🚫 Bloklandi. Blokdan chiqarish: /blocked",
        "unblocked_ok": "✅ Blokdan chiqarildi.",
        "blocked_list_title": "🚫 <b>Bloklanganlar</b> — {count} ta\n\nBlokdan chiqarish uchun bosing:",
        "blocked_empty": "✅ Siz hech kimni bloklamagansiz.",
        "blocked_item": "👤 #{num} — {count} ta xabar",
        "share_text": "Menga anonim xabar yozing! 👇",
        # tugmalar
        "btn_share": "🔗 Havolani ulashish",
        "btn_cancel_send": "Yuborishni bekor qilish",
        "btn_delete": "🗑 Xabarni o'chirish",
        "btn_reply": "✍️ Javob berish",
        "btn_block": "🚫 Bloklash",
        "btn_yes": "✅ Ha, yangilansin",
        "btn_no": "❌ Yo'q",
        "btn_settings": "⚙️ Sozlamalar",
        "btn_help": "❓ Yordam",
        "btn_stats": "📊 Statistika",
        "btn_prev": "◀️ Oldingi",
        "btn_next": "Keyingi ▶️",
        "btn_back": "⬅️ Orqaga",
        "btn_lang": "🌐 Til",
        "btn_accepting": "🔔 Qabul qilish: {state}",
        "btn_blocked": "🚫 Bloklanganlar",
        "btn_cancel": "❌ Bekor qilish",
        # admin
        # --- yangi tugmalar
        "btn_make_image": "🖼 Rasm qilish",
        "btn_send_more": "✍️ Yana xabar yuborish",
        "btn_unsend": "🗑 Xabarni o'chirish",
        "btn_write_self": "✍️ O'zimga yozib ko'rish",
        "btn_refresh": "🔄 Yangilash",
        "btn_close": "❌ Yopish",
        # --- yuborilgan xabarni qaytarib olish
        "unsent_ok": "🗑 Xabaringiz o'chirildi — qabul qiluvchida ham ko'rinmaydi.",
        "unsend_failed": (
            "⚠️ O'chirib bo'lmadi. Telegram botlarga faqat 48 soat ichidagi "
            "xabarlarni o'chirishga ruxsat beradi."
        ),
        "img_no_text": "⚠️ Rasm faqat matnli xabarlardan yasaladi.",
        "img_failed": "⚠️ Rasm yasalmadi.",
        # --- admin panel
        "admin_home": (
            "🛠 <b>Admin panel</b>\n\n"
            "👥 Foydalanuvchilar: <b>{users}</b>\n"
            "💬 Xabarlar: <b>{messages}</b>\n"
            "👮 Adminlar: <b>{admins}</b>"
        ),
        "btn_adm_stats": "📊 Statistika",
        "btn_adm_broadcast": "📣 Xabar yuborish",
        "btn_adm_users": "👥 Foydalanuvchilar",
        "btn_users_csv": "📤 Ro'yxatni yuklab olish",
        "users_title": (
            "👥 <b>Foydalanuvchilar</b> — {total} ta\n"
            "<blockquote>✅ Faol: {active}\n"
            "🔕 Botni to'xtatgan: {stopped}\n"
            "🆕 Bugun qo'shilgan: {today}</blockquote>\n"
            "{rows}"
        ),
        "users_row": "{num}. {name} — <code>{uid}</code>\n     💬 {got} · 📤 {sent} · 📅 {date}",
        "users_empty": "👥 Hali foydalanuvchi yo'q.",
        "users_csv_caption": "👥 Barcha foydalanuvchilar — {total} ta",
        "btn_adm_admins": "👮 Adminlar",
        "btn_adm_emoji": "😀 Emojilar",
        "btn_adm_add": "➕ Admin qo'shish",
        "admins_title": (
            "👮 <b>Adminlar</b>\n\n"
            "❌ bosilsa — admin olib tashlanadi.\n"
            "🔒 — .env faylidagi asosiy adminlar, ularni bu yerdan o'chirib bo'lmaydi."
        ),
        "admin_add_prompt": (
            "➕ <b>Yangi admin</b>\n\n"
            "Uning Telegram ID raqamini yuboring (masalan <code>123456789</code>),\n"
            "yoki o'sha odamning istalgan xabarini shu yerga <b>forward</b> qiling.\n\n"
            "Bekor qilish — /admin"
        ),
        "admin_added": "✅ <code>{uid}</code> admin qilib qo'shildi.",
        "admin_removed": "✅ <code>{uid}</code> adminlikdan olindi.",
        "admin_exists": "ℹ️ Bu foydalanuvchi allaqachon admin.",
        "admin_bad_id": "⚠️ ID topilmadi. Raqam yuboring yoki xabarini forward qiling.",
        "admin_is_owner": "🔒 Bu asosiy admin — .env faylidan o'chiriladi.",
        "admin_forward_hidden": (
            "⚠️ Bu odam maxfiylik sozlamasi tufayli forward orqali aniqlanmadi. "
            "ID raqamini yozing."
        ),
        # --- emoji sozlagich
        "emoji_title": (
            "😀 <b>Emojilar</b>\n\n"
            "Hozirgi ko'rinishi:\n{preview}\n\n"
            "O'zgartirmoqchi bo'lganini tanlang.\n"
            "<blockquote>Premium emoji bot xabarlarida ham, tugmalarda ham "
            "chiqadi — buning uchun bot egasida Telegram Premium bo'lishi kerak."
            "</blockquote>"
        ),
        "emoji_pick": (
            "😀 <b>{emoji}</b> — <i>{title}</i>\n\n"
            "Yangi emojini shu yerga yuboring.\n\n"
            "⭐️ <b>Premium emoji</b> ham bo'ladi: Telegram Premium hisobingizdan "
            "o'sha emojini yuboring.\n"
            "<blockquote>Shart: bot egasida Telegram Premium bo'lsa (yoki bot "
            "username'i Fragment'dan olingan bo'lsa) — premium emoji xabarlarda "
            "ham, tugmalarda ham chiqadi.</blockquote>"
        ),
        "emoji_saved": "✅ Saqlandi: {emoji} → {new}",
        "emoji_saved_custom": (
            "✅ Saqlandi: {emoji} → premium emoji (ID <code>{new}</code>)\n\n"
            "☝️ <b>Sinov xabariga va quyidagi tugmalarga qarang.</b>\n"
            "<blockquote>Jonli (animatsiyali) chiqsa — ishlayapti.\n"
            "Oddiy {base} ko'rinishida chiqsa — bot egasida Telegram Premium "
            "yo'q, lekin emoji baribir {base} ga almashdi.</blockquote>"
        ),
        "emoji_need_emoji": "⚠️ Faqat bitta emoji yuboring.",
        "emoji_reset_ok": "♻️ Asliga qaytarildi.",
        "emoji_resetall_ok": "♻️ Barcha emojilar asliga qaytarildi.",
        "btn_emoji_reset": "♻️ Asliga qaytarish",
        "btn_emoji_resetall": "♻️ Hammasini asliga qaytarish",
        "emoji_custom_failed": (
            "⚠️ Premium emoji ishlamadi — Telegram bu botga ruxsat bermadi.\n"
            "Bot egasida Telegram Premium bo'lishi kerak (yoki bot username'i "
            "Fragment'dan olingan bo'lishi). Emojilar oddiy holatga qaytarildi."
        ),
        # --- majburiy obuna
        "sub_required": (
            "📢 <b>Botdan foydalanish uchun avval quyidagiga a'zo bo'ling:</b>\n"
            "<blockquote>A'zo bo'lgach «Tekshirish» tugmasini bosing.</blockquote>"
        ),
        "sub_fail": "⚠️ Hali hammasiga a'zo bo'lmadingiz. Tekshirib qayta bosing.",
        "sub_ok": "✅ Rahmat! Endi botdan to'liq foydalanishingiz mumkin.",
        "btn_sub_check": "✅ Tekshirish",
        # --- kanallar (admin)
        "btn_adm_channels": "📢 Kanallar",
        "btn_adm_channel_add": "➕ Kanal qo'shish",
        "channels_title": (
            "📢 <b>Majburiy obuna</b> — {count} ta kanal\n\n"
            "❌ bosilsa kanal ro'yxatdan olinadi.\n"
            "<blockquote>Ro'yxat bo'sh bo'lsa majburiy obuna o'chiq bo'ladi.</blockquote>"
        ),
        "channels_empty": (
            "📢 <b>Majburiy obuna</b>\n\n"
            "Hozircha kanal qo'shilmagan — obuna talab qilinmaydi."
        ),
        "channel_add_prompt": (
            "➕ <b>Kanal qo'shish</b>\n\n"
            "Kanaldan istalgan postni shu yerga <b>forward</b> qiling,\n"
            "yoki kanal manzilini yozing: <code>@kanal_nomi</code>\n\n"
            "⚠️ Bot o'sha kanalda <b>admin</b> bo'lishi shart — aks holda a'zolikni "
            "tekshira olmaydi.\n\nBekor qilish — /admin"
        ),
        "channel_added": "✅ Qo'shildi: <b>{title}</b>",
        "channel_removed": "✅ Kanal ro'yxatdan olindi.",
        "channel_bad": "⚠️ Kanal aniqlanmadi. Postni forward qiling yoki @nomini yuboring.",
        "channel_not_admin": (
            "⚠️ Bot bu kanalda admin emas yoki kanalga kira olmadi.\n"
            "Avval botni kanalga admin qiling, so'ng qayta urinib ko'ring."
        ),
        # --- shikoyat va ban
        "btn_report": "⚠️ Shikoyat",
        "report_sent": "✅ Shikoyatingiz adminlarga yuborildi.",
        "report_already": "ℹ️ Bu xabar uchun shikoyat allaqachon yuborilgan.",
        "admin_report": (
            "⚠️ <b>Yangi shikoyat</b>\n"
            "<blockquote>{text}</blockquote>\n"
            "Muallifni banlasangiz, u boshqa hech kimga anonim yoza olmaydi."
        ),
        "btn_ban": "🚫 Banlash",
        "btn_ignore": "✅ E'tiborsiz",
        "ban_done": "🚫 Muallif banlandi.",
        "report_closed": "✅ Shikoyat yopildi.",
        "you_are_banned": (
            "🚫 <b>Siz botdan foydalana olmaysiz.</b>\n"
            "Anonim xabar yuborish huquqingiz adminlar tomonidan cheklangan."
        ),
        "btn_adm_banned": "🚫 Banlanganlar",
        "banned_title": "🚫 <b>Banlanganlar</b> — {count} ta\n\nBanni olish uchun bosing:",
        "banned_empty": "✅ Banlangan foydalanuvchi yo'q.",
        "unban_done": "✅ Ban olib tashlandi.",
        # --- broadcast
        "bc_target": "📣 <b>Xabar yuborish</b>\n\nKimga yuboramiz?",
        "btn_bc_all": "👥 Hammaga ({n})",
        "btn_bc_active": "✅ Faollarga ({n})",
        "btn_bc_got": "💬 Xabar olganlarga ({n})",
        "bc_ask": "📣 Yuboriladigan xabarni tashlang.\n\nBekor qilish — /admin",
        "bc_preview": (
            "📣 <b>Yuborishdan oldin ko'rib chiqing</b>\n"
            "<blockquote>Yuqoridagi xabar <b>{n}</b> ta foydalanuvchiga ketadi.</blockquote>"
        ),
        "btn_bc_send": "📤 Yuborish",
        "bc_progress": "📤 <b>Yuborilmoqda…</b>\n\n{done} / {total}\n✅ {ok}  ❌ {failed}",
        "btn_bc_stop": "⛔️ To'xtatish",
        "bc_stopped": "⛔️ To'xtatildi.",
        # --- bot sozlamalari
        "btn_adm_settings": "⚙️ Bot sozlamalari",
        "bot_settings_title": (
            "⚙️ <b>Bot sozlamalari</b>\n\n"
            "Bosib yoqing yoki o'chiring. O'zgarish darhol kuchga kiradi.\n"
            "<blockquote>Bu yerdagi sozlamalar config.py dagidan ustun turadi.</blockquote>"
        ),
        "set_reply_btn": "Javob berish tugmasi",
        "set_block_btn": "Bloklash tugmasi",
        "set_image_btn": "Rasm qilish tugmasi",
        "set_delete_btn": "O'chirish tugmasi",
        "set_auto_image": "Rasmni avtomatik yuborish",
        "set_colors": "Rangli tugmalar",
        "set_report_btn": "Shikoyat tugmasi",
        # --- zaxira va kunlik statistika
        "btn_adm_backup": "💾 Zaxira nusxa",
        "backup_caption": "💾 Baza zaxirasi — {date}\n👥 {users} foydalanuvchi · 💬 {messages} xabar",
        "backup_failed": "⚠️ Zaxira olinmadi: {error}",
        "btn_adm_daily": "📈 Kunlik",
        "daily_title": (
            "📈 <b>Oxirgi {days} kun</b>\n"
            "<blockquote>👥 yangi · 💬 xabar · 👀 o'tish</blockquote>\n"
            "<pre>{chart}</pre>"
        ),
        "btn_daily_7": "📈 7 kun",
        "btn_daily_30": "📈 30 kun",
        "admin_only": "⛔️ Bu buyruq faqat adminlar uchun.",
        "admin_stats": (
            "📊 <b>Umumiy statistika</b>\n\n"
            "👥 Foydalanuvchilar: <b>{users}</b>\n"
            "✅ Faol: <b>{active_users}</b>\n"
            "🆕 Bugun qo'shilgan: <b>{new_today}</b>\n\n"
            "💬 Barcha xabarlar: <b>{messages}</b>\n"
            "📅 Bugun: <b>{messages_today}</b>\n"
            "👀 Havola o'tishlari: <b>{views}</b>\n"
            "🚫 Bloklar: <b>{blocks}</b>"
        ),
        "admin_issue": "💡 <b>Yangi g'oya</b> (ID <code>{uid}</code>):\n\n{text}",
        "broadcast_prompt": "📣 Barchaga yuborish uchun xabarni tashlang.\nBekor qilish — /cancel",
        "broadcast_started": "⏳ Yuborish boshlandi...",
        "broadcast_done": "✅ Tayyor!\n\n📤 Yuborildi: <b>{ok}</b>\n❌ Yetib bormadi: <b>{failed}</b>",
    },
    # ================================================================ RU
    "ru": {
        "start_main": (
            "Начните получать анонимные сообщения прямо сейчас 🚀\n\n"
            "Ваша ссылка 👇\n"
            "<blockquote>{link}</blockquote>\n"
            "<b>Разместите эту ссылку ☝️ в описании профиля 📱/🎵/📷, "
            "и вам начнут приходить анонимные сообщения</b> 💬"
        ),
        "anon_prompt": (
            "🔗 Здесь можно отправить <b>анонимное сообщение</b> человеку, "
            "который разместил эту ссылку.\n\n"
            "💡 <b>Напишите сюда всё, что хотите ему передать</b>, и через "
            "несколько секунд он получит ваше сообщение, но не узнает, от кого.\n"
            "<blockquote>Можно отправить: текст, фото, видео, стикеры, "
            "голосовые и видеосообщения (кружки)</blockquote>"
        ),
        "sent_ok": "✅ Сообщение отправлено, ждите ответа!",
        "reply_sent": "✅ Ответ отправлен!",
        "incoming_text": (
            "💬 <b>Вам новое анонимное сообщение!</b>\n"
            "<blockquote>{text}</blockquote>\n"
            "↩️ <i>Свайпните, чтобы ответить.</i>"
        ),
        "incoming_media": (
            "💬 <b>Вам новое анонимное сообщение!</b>\n"
            "↩️ <i>Свайпните, чтобы ответить.</i>"
        ),
        "reply_text": (
            "✉️ <b>Пришёл ответ на ваше анонимное сообщение!</b>\n"
            "<blockquote>{text}</blockquote>\n"
            "↩️ <i>Свайпните, чтобы ответить.</i>"
        ),
        "reply_media": (
            "✉️ <b>Пришёл ответ на ваше анонимное сообщение!</b>\n"
            "↩️ <i>Свайпните, чтобы ответить.</i>"
        ),
        "mystats": (
            "📊 <b>Статистика профиля</b>\n\n"
            "🔹 <b>Сегодня:</b>\n"
            "<blockquote>💬 Сообщений: {msg_today}\n"
            "👀 Переходов по ссылке: {views_today}\n"
            "👑 Популярность: {pop_today}/10</blockquote>\n"
            "🔹 <b>За всё время:</b>\n"
            "<blockquote>💬 Сообщений: {msg_total}\n"
            "👀 Переходов по ссылке: {views_total}\n"
            "👑 Популярность: {pop_total}/10</blockquote>\n"
            "⭐️ <i>Чтобы поднять популярность, распространяйте "
            "свою личную ссылку:</i>\n👉 {link}"
        ),
        "url_ask": (
            "🔗 <b>Обновить ссылку?</b>\n\n"
            "Текущая ссылка:\n<blockquote>{link}</blockquote>\n"
            "⚠️ После обновления <b>старая ссылка перестанет работать</b> — "
            "её нужно будет заменить и в профиле."
        ),
        "url_changed": (
            "✅ <b>Ссылка обновлена!</b>\n"
            "<blockquote>{link}</blockquote>\n"
            "Старая ссылка больше не работает."
        ),
        "issue_prompt": (
            "💡 <b>Напишите идею или проблему</b> — я передам её владельцу бота.\n\n"
            "Для отмены нажмите /start."
        ),
        "issue_sent": "✅ Спасибо! Ваше сообщение передано.",
        "issue_nowhere": "⚠️ Приём идей пока не настроен.",
        "help": (
            "❓ <b>Как работает бот?</b>\n\n"
            "1️⃣ Размещаете личную ссылку в профиле.\n"
            "2️⃣ Друзья открывают её и пишут вам анонимно.\n"
            "3️⃣ Сообщение приходит вам — автор неизвестен.\n"
            "4️⃣ Чтобы ответить, <b>свайпните</b> это сообщение (ответьте на него).\n\n"
            "<b>Команды:</b>\n"
            "/start — получить ссылку\n"
            "/mystats — ваша статистика\n"
            "/url — обновить ссылку\n"
            "/issue — идея или жалоба\n"
            "/settings — настройки (язык, блокировки)"
        ),
        "self_not_allowed": "🙃 Нельзя написать анонимно самому себе.",
        "user_not_found": "❓ Пользователь не найден. Возможно, ссылка устарела.",
        "not_accepting": "🔕 Этот пользователь пока не принимает анонимные сообщения.",
        "you_are_blocked": "🚫 Пользователь заблокировал вас, сообщение не дойдёт.",
        "receiver_unavailable": "⚠️ Не удалось доставить — пользователь остановил или заблокировал бота.",
        "msg_not_found": "⚠️ Сообщение не найдено или слишком старое.",
        "reply_prompt": "✍️ Напишите ответ — он уйдёт анонимно.",
        "reply_hint": "↩️ Чтобы ответить, <b>свайпните пришедшее сообщение</b> и напишите ответ.",
        "unsupported": "⚠️ Такой тип сообщения отправить нельзя. Попробуйте другой.",
        "flood": "🐢 Слишком быстро, немного подождите.",
        "cancelled": "❌ Отменено.",
        "nothing_to_cancel": "ℹ️ Сейчас нечего отменять.",
        "deleted_ok": "🗑 Сообщение удалено.",
        "settings_title": (
            "⚙️ <b>Настройки</b>\n\n"
            "🌐 Язык: {lang}\n"
            "🔔 Анонимные сообщения: {accepting}\n"
            "🚫 В блоке: {blocked}"
        ),
        "on": "включены ✅",
        "off": "выключены ❌",
        "lang_choose": "🌐 Выберите язык:",
        "lang_set": "✅ Язык изменён.",
        "accepting_on": "🔔 Анонимные сообщения снова принимаются.",
        "accepting_off": "🔕 Анонимные сообщения временно отключены.",
        "blocked_ok": "🚫 Заблокирован. Разблокировать: /blocked",
        "unblocked_ok": "✅ Разблокирован.",
        "blocked_list_title": "🚫 <b>Заблокированные</b> — {count}\n\nНажмите, чтобы разблокировать:",
        "blocked_empty": "✅ Вы никого не блокировали.",
        "blocked_item": "👤 #{num} — сообщений: {count}",
        "share_text": "Напиши мне анонимно! 👇",
        "btn_share": "🔗 Поделиться ссылкой",
        "btn_cancel_send": "Отменить отправку",
        "btn_delete": "🗑 Удалить сообщение",
        "btn_reply": "✍️ Ответить",
        "btn_block": "🚫 Заблокировать",
        "btn_yes": "✅ Да, обновить",
        "btn_no": "❌ Нет",
        "btn_settings": "⚙️ Настройки",
        "btn_help": "❓ Помощь",
        "btn_stats": "📊 Статистика",
        "btn_prev": "◀️ Назад",
        "btn_next": "Вперёд ▶️",
        "btn_back": "⬅️ Назад",
        "btn_lang": "🌐 Язык",
        "btn_accepting": "🔔 Приём: {state}",
        "btn_blocked": "🚫 Заблокированные",
        "btn_cancel": "❌ Отмена",
        "btn_make_image": "🖼 Сделать картинку",
        "btn_send_more": "✍️ Написать ещё",
        "btn_unsend": "🗑 Удалить сообщение",
        "btn_write_self": "✍️ Написать себе",
        "btn_refresh": "🔄 Обновить",
        "btn_close": "❌ Закрыть",
        "unsent_ok": "🗑 Ваше сообщение удалено — получатель его больше не видит.",
        "unsend_failed": (
            "⚠️ Не удалось удалить. Telegram разрешает ботам удалять сообщения "
            "только в течение 48 часов."
        ),
        "img_no_text": "⚠️ Картинка делается только из текстовых сообщений.",
        "img_failed": "⚠️ Не удалось создать картинку.",
        "admin_home": (
            "🛠 <b>Админ-панель</b>\n\n"
            "👥 Пользователей: <b>{users}</b>\n"
            "💬 Сообщений: <b>{messages}</b>\n"
            "👮 Админов: <b>{admins}</b>"
        ),
        "btn_adm_stats": "📊 Статистика",
        "btn_adm_broadcast": "📣 Рассылка",
        "btn_adm_users": "👥 Пользователи",
        "btn_users_csv": "📤 Скачать список",
        "users_title": (
            "👥 <b>Пользователи</b> — {total}\n"
            "<blockquote>✅ Активных: {active}\n"
            "🔕 Остановили бота: {stopped}\n"
            "🆕 Новых сегодня: {today}</blockquote>\n"
            "{rows}"
        ),
        "users_row": "{num}. {name} — <code>{uid}</code>\n     💬 {got} · 📤 {sent} · 📅 {date}",
        "users_empty": "👥 Пользователей пока нет.",
        "users_csv_caption": "👥 Все пользователи — {total}",
        "btn_adm_admins": "👮 Админы",
        "btn_adm_emoji": "😀 Эмодзи",
        "btn_adm_add": "➕ Добавить админа",
        "admins_title": (
            "👮 <b>Админы</b>\n\n"
            "❌ — убрать из админов.\n"
            "🔒 — главные админы из .env, их отсюда убрать нельзя."
        ),
        "admin_add_prompt": (
            "➕ <b>Новый админ</b>\n\n"
            "Пришлите его Telegram ID (например <code>123456789</code>)\n"
            "или перешлите сюда любое его сообщение.\n\n"
            "Отмена — /admin"
        ),
        "admin_added": "✅ <code>{uid}</code> добавлен в админы.",
        "admin_removed": "✅ <code>{uid}</code> убран из админов.",
        "admin_exists": "ℹ️ Этот пользователь уже админ.",
        "admin_bad_id": "⚠️ ID не найден. Пришлите число или перешлите сообщение.",
        "admin_is_owner": "🔒 Это главный админ — убирается из файла .env.",
        "admin_forward_hidden": (
            "⚠️ Из-за настроек приватности пользователь не определился. "
            "Пришлите его ID числом."
        ),
        "emoji_title": (
            "😀 <b>Эмодзи</b>\n\n"
            "Сейчас выглядит так:\n{preview}\n\n"
            "Выберите, какой менять.\n"
            "<blockquote>Премиум-эмодзи работают и в сообщениях, и на кнопках — "
            "нужно, чтобы у владельца бота был Telegram Premium.</blockquote>"
        ),
        "emoji_pick": (
            "😀 <b>{emoji}</b> — <i>{title}</i>\n\n"
            "Пришлите новый эмодзи сюда.\n\n"
            "⭐️ <b>Премиум-эмодзи</b> тоже можно: отправьте его с Premium-аккаунта.\n"
            "<blockquote>Условие: у владельца бота есть Telegram Premium (или "
            "юзернейм бота куплен на Fragment) — тогда премиум-эмодзи работают "
            "и в сообщениях, и на кнопках.</blockquote>"
        ),
        "emoji_saved": "✅ Сохранено: {emoji} → {new}",
        "emoji_saved_custom": (
            "✅ Сохранено: {emoji} → премиум-эмодзи (ID <code>{new}</code>)\n\n"
            "☝️ <b>Посмотрите на тестовое сообщение и кнопки ниже.</b>\n"
            "<blockquote>Анимированное — работает.\n"
            "Обычное {base} — у владельца бота нет Telegram Premium, но эмодзи "
            "всё равно заменилось на {base}.</blockquote>"
        ),
        "emoji_need_emoji": "⚠️ Пришлите ровно один эмодзи.",
        "emoji_reset_ok": "♻️ Возвращено к исходному.",
        "emoji_resetall_ok": "♻️ Все эмодзи возвращены к исходным.",
        "btn_emoji_reset": "♻️ Вернуть исходный",
        "btn_emoji_resetall": "♻️ Вернуть все",
        "emoji_custom_failed": (
            "⚠️ Премиум-эмодзи не сработали — Telegram не разрешил этому боту.\n"
            "У владельца бота должен быть Telegram Premium (или юзернейм с "
            "Fragment). Эмодзи возвращены к обычным."
        ),
        "sub_required": (
            "📢 <b>Чтобы пользоваться ботом, подпишитесь:</b>\n"
            "<blockquote>После подписки нажмите «Проверить».</blockquote>"
        ),
        "sub_fail": "⚠️ Вы подписаны не на всё. Подпишитесь и нажмите ещё раз.",
        "sub_ok": "✅ Спасибо! Теперь бот доступен полностью.",
        "btn_sub_check": "✅ Проверить",
        "btn_adm_channels": "📢 Каналы",
        "btn_adm_channel_add": "➕ Добавить канал",
        "channels_title": (
            "📢 <b>Обязательная подписка</b> — каналов: {count}\n\n"
            "❌ убирает канал из списка.\n"
            "<blockquote>Если список пуст, подписка не требуется.</blockquote>"
        ),
        "channels_empty": (
            "📢 <b>Обязательная подписка</b>\n\n"
            "Каналы не добавлены — подписка не требуется."
        ),
        "channel_add_prompt": (
            "➕ <b>Добавить канал</b>\n\n"
            "Перешлите сюда любой пост из канала,\n"
            "или напишите адрес: <code>@имя_канала</code>\n\n"
            "⚠️ Бот должен быть <b>админом</b> этого канала, иначе он не сможет "
            "проверять подписку.\n\nОтмена — /admin"
        ),
        "channel_added": "✅ Добавлен: <b>{title}</b>",
        "channel_removed": "✅ Канал убран из списка.",
        "channel_bad": "⚠️ Канал не определён. Перешлите пост или пришлите @имя.",
        "channel_not_admin": (
            "⚠️ Бот не админ в этом канале или не имеет к нему доступа.\n"
            "Сделайте бота админом канала и попробуйте снова."
        ),
        "btn_report": "⚠️ Пожаловаться",
        "report_sent": "✅ Жалоба отправлена админам.",
        "report_already": "ℹ️ На это сообщение жалоба уже отправлена.",
        "admin_report": (
            "⚠️ <b>Новая жалоба</b>\n"
            "<blockquote>{text}</blockquote>\n"
            "Если забаните автора, он больше никому не сможет писать анонимно."
        ),
        "btn_ban": "🚫 Забанить",
        "btn_ignore": "✅ Игнорировать",
        "ban_done": "🚫 Автор забанен.",
        "report_closed": "✅ Жалоба закрыта.",
        "you_are_banned": (
            "🚫 <b>Вы не можете пользоваться ботом.</b>\n"
            "Админы ограничили вам отправку анонимных сообщений."
        ),
        "btn_adm_banned": "🚫 Забаненные",
        "banned_title": "🚫 <b>Забаненные</b> — {count}\n\nНажмите, чтобы разбанить:",
        "banned_empty": "✅ Забаненных нет.",
        "unban_done": "✅ Бан снят.",
        "bc_target": "📣 <b>Рассылка</b>\n\nКому отправляем?",
        "btn_bc_all": "👥 Всем ({n})",
        "btn_bc_active": "✅ Активным ({n})",
        "btn_bc_got": "💬 Получавшим сообщения ({n})",
        "bc_ask": "📣 Пришлите сообщение для рассылки.\n\nОтмена — /admin",
        "bc_preview": (
            "📣 <b>Проверьте перед отправкой</b>\n"
            "<blockquote>Сообщение выше уйдёт <b>{n}</b> пользователям.</blockquote>"
        ),
        "btn_bc_send": "📤 Отправить",
        "bc_progress": "📤 <b>Отправка…</b>\n\n{done} / {total}\n✅ {ok}  ❌ {failed}",
        "btn_bc_stop": "⛔️ Остановить",
        "bc_stopped": "⛔️ Остановлено.",
        "btn_adm_settings": "⚙️ Настройки бота",
        "bot_settings_title": (
            "⚙️ <b>Настройки бота</b>\n\n"
            "Нажмите, чтобы включить или выключить. Применяется сразу.\n"
            "<blockquote>Эти настройки важнее того, что указано в config.py.</blockquote>"
        ),
        "set_reply_btn": "Кнопка «Ответить»",
        "set_block_btn": "Кнопка «Заблокировать»",
        "set_image_btn": "Кнопка «Сделать картинку»",
        "set_delete_btn": "Кнопка «Удалить»",
        "set_auto_image": "Картинка автоматически",
        "set_colors": "Цветные кнопки",
        "set_report_btn": "Кнопка «Пожаловаться»",
        "btn_adm_backup": "💾 Резервная копия",
        "backup_caption": "💾 Копия базы — {date}\n👥 {users} польз. · 💬 {messages} сообщ.",
        "backup_failed": "⚠️ Не удалось сделать копию: {error}",
        "btn_adm_daily": "📈 По дням",
        "daily_title": (
            "📈 <b>Последние {days} дней</b>\n"
            "<blockquote>👥 новые · 💬 сообщения · 👀 переходы</blockquote>\n"
            "<pre>{chart}</pre>"
        ),
        "btn_daily_7": "📈 7 дней",
        "btn_daily_30": "📈 30 дней",
        "admin_only": "⛔️ Команда только для админов.",
        "admin_stats": (
            "📊 <b>Общая статистика</b>\n\n"
            "👥 Пользователей: <b>{users}</b>\n"
            "✅ Активных: <b>{active_users}</b>\n"
            "🆕 Новых сегодня: <b>{new_today}</b>\n\n"
            "💬 Всего сообщений: <b>{messages}</b>\n"
            "📅 Сегодня: <b>{messages_today}</b>\n"
            "👀 Переходов: <b>{views}</b>\n"
            "🚫 Блокировок: <b>{blocks}</b>"
        ),
        "admin_issue": "💡 <b>Новая идея</b> (ID <code>{uid}</code>):\n\n{text}",
        "broadcast_prompt": "📣 Пришлите сообщение для рассылки.\nОтмена — /cancel",
        "broadcast_started": "⏳ Рассылка началась...",
        "broadcast_done": "✅ Готово!\n\n📤 Доставлено: <b>{ok}</b>\n❌ Не дошло: <b>{failed}</b>",
    },
    # ================================================================ EN
    "en": {
        "start_main": (
            "Start receiving anonymous messages right now 🚀\n\n"
            "Your link 👇\n"
            "<blockquote>{link}</blockquote>\n"
            "<b>Put this link ☝️ in your 📱/🎵/📷 profile bio and you'll start "
            "getting anonymous messages</b> 💬"
        ),
        "anon_prompt": (
            "🔗 Here you can send an <b>anonymous message</b> to the person "
            "who shared this link.\n\n"
            "💡 <b>Write everything you want to tell them right here</b>, and in a "
            "few seconds they will get your message without knowing who sent it.\n"
            "<blockquote>You can send: text, photos, video, stickers, "
            "voice and video messages (round)</blockquote>"
        ),
        "sent_ok": "✅ Message sent, wait for a reply!",
        "reply_sent": "✅ Reply sent!",
        "incoming_text": (
            "💬 <b>You have a new anonymous message!</b>\n"
            "<blockquote>{text}</blockquote>\n"
            "↩️ <i>Swipe to reply.</i>"
        ),
        "incoming_media": (
            "💬 <b>You have a new anonymous message!</b>\n"
            "↩️ <i>Swipe to reply.</i>"
        ),
        "reply_text": (
            "✉️ <b>You got a reply to your anonymous message!</b>\n"
            "<blockquote>{text}</blockquote>\n"
            "↩️ <i>Swipe to reply.</i>"
        ),
        "reply_media": (
            "✉️ <b>You got a reply to your anonymous message!</b>\n"
            "↩️ <i>Swipe to reply.</i>"
        ),
        "mystats": (
            "📊 <b>Profile statistics</b>\n\n"
            "🔹 <b>Today:</b>\n"
            "<blockquote>💬 Messages: {msg_today}\n"
            "👀 Link opens: {views_today}\n"
            "👑 Popularity: {pop_today}/10</blockquote>\n"
            "🔹 <b>All time:</b>\n"
            "<blockquote>💬 Messages: {msg_total}\n"
            "👀 Link opens: {views_total}\n"
            "👑 Popularity: {pop_total}/10</blockquote>\n"
            "⭐️ <i>Share your personal link to raise your popularity:</i>\n👉 {link}"
        ),
        "url_ask": (
            "🔗 <b>Update your link?</b>\n\n"
            "Current link:\n<blockquote>{link}</blockquote>\n"
            "⚠️ After updating, <b>the old link stops working</b> — "
            "you'll need to replace it in your bio too."
        ),
        "url_changed": (
            "✅ <b>Your link has been updated!</b>\n"
            "<blockquote>{link}</blockquote>\n"
            "The old link no longer works."
        ),
        "issue_prompt": (
            "💡 <b>Write your idea or problem</b> — I'll pass it to the bot owner.\n\n"
            "Press /start to cancel."
        ),
        "issue_sent": "✅ Thanks! Your message has been delivered.",
        "issue_nowhere": "⚠️ Idea collection isn't set up yet.",
        "help": (
            "❓ <b>How does it work?</b>\n\n"
            "1️⃣ Put your personal link in your bio.\n"
            "2️⃣ Friends open it and write to you anonymously.\n"
            "3️⃣ The message arrives here — the sender stays unknown.\n"
            "4️⃣ To answer, <b>swipe</b> that message (reply to it) and write back.\n\n"
            "<b>Commands:</b>\n"
            "/start — get your link\n"
            "/mystats — your statistics\n"
            "/url — update your link\n"
            "/issue — idea or complaint\n"
            "/settings — settings (language, blocked list)"
        ),
        "self_not_allowed": "🙃 You can't send an anonymous message to yourself.",
        "user_not_found": "❓ User not found. The link may be outdated.",
        "not_accepting": "🔕 This user is not accepting anonymous messages right now.",
        "you_are_blocked": "🚫 This user has blocked you, the message won't arrive.",
        "receiver_unavailable": "⚠️ Couldn't deliver — the user stopped or blocked the bot.",
        "msg_not_found": "⚠️ This message was not found or is too old.",
        "reply_prompt": "✍️ Write your reply — it will be sent anonymously.",
        "reply_hint": "↩️ To answer, <b>swipe the message you received</b> and write your reply.",
        "unsupported": "⚠️ This message type can't be sent. Try another one.",
        "flood": "🐢 Too fast, please slow down a bit.",
        "cancelled": "❌ Cancelled.",
        "nothing_to_cancel": "ℹ️ Nothing to cancel right now.",
        "deleted_ok": "🗑 Message deleted.",
        "settings_title": (
            "⚙️ <b>Settings</b>\n\n"
            "🌐 Language: {lang}\n"
            "🔔 Anonymous messages: {accepting}\n"
            "🚫 Blocked: {blocked}"
        ),
        "on": "on ✅",
        "off": "off ❌",
        "lang_choose": "🌐 Choose a language:",
        "lang_set": "✅ Language changed.",
        "accepting_on": "🔔 Anonymous messages are accepted again.",
        "accepting_off": "🔕 Anonymous messages are temporarily off.",
        "blocked_ok": "🚫 Blocked. To unblock: /blocked",
        "unblocked_ok": "✅ Unblocked.",
        "blocked_list_title": "🚫 <b>Blocked</b> — {count}\n\nTap to unblock:",
        "blocked_empty": "✅ You haven't blocked anyone.",
        "blocked_item": "👤 #{num} — {count} messages",
        "share_text": "Send me an anonymous message! 👇",
        "btn_share": "🔗 Share the link",
        "btn_cancel_send": "Cancel sending",
        "btn_delete": "🗑 Delete message",
        "btn_reply": "✍️ Reply",
        "btn_block": "🚫 Block",
        "btn_yes": "✅ Yes, update",
        "btn_no": "❌ No",
        "btn_settings": "⚙️ Settings",
        "btn_help": "❓ Help",
        "btn_stats": "📊 Statistics",
        "btn_prev": "◀️ Prev",
        "btn_next": "Next ▶️",
        "btn_back": "⬅️ Back",
        "btn_lang": "🌐 Language",
        "btn_accepting": "🔔 Receiving: {state}",
        "btn_blocked": "🚫 Blocked list",
        "btn_cancel": "❌ Cancel",
        "btn_make_image": "🖼 Make an image",
        "btn_send_more": "✍️ Send another",
        "btn_unsend": "🗑 Delete message",
        "btn_write_self": "✍️ Write to myself",
        "btn_refresh": "🔄 Refresh",
        "btn_close": "❌ Close",
        "unsent_ok": "🗑 Your message was deleted — the recipient can't see it anymore.",
        "unsend_failed": (
            "⚠️ Couldn't delete. Telegram only lets bots delete messages "
            "within 48 hours."
        ),
        "img_no_text": "⚠️ Images are made from text messages only.",
        "img_failed": "⚠️ Couldn't create the image.",
        "admin_home": (
            "🛠 <b>Admin panel</b>\n\n"
            "👥 Users: <b>{users}</b>\n"
            "💬 Messages: <b>{messages}</b>\n"
            "👮 Admins: <b>{admins}</b>"
        ),
        "btn_adm_stats": "📊 Statistics",
        "btn_adm_broadcast": "📣 Broadcast",
        "btn_adm_users": "👥 Users",
        "btn_users_csv": "📤 Download the list",
        "users_title": (
            "👥 <b>Users</b> — {total}\n"
            "<blockquote>✅ Active: {active}\n"
            "🔕 Stopped the bot: {stopped}\n"
            "🆕 New today: {today}</blockquote>\n"
            "{rows}"
        ),
        "users_row": "{num}. {name} — <code>{uid}</code>\n     💬 {got} · 📤 {sent} · 📅 {date}",
        "users_empty": "👥 No users yet.",
        "users_csv_caption": "👥 All users — {total}",
        "btn_adm_admins": "👮 Admins",
        "btn_adm_emoji": "😀 Emojis",
        "btn_adm_add": "➕ Add admin",
        "admins_title": (
            "👮 <b>Admins</b>\n\n"
            "❌ removes an admin.\n"
            "🔒 are the main admins from .env, they can't be removed here."
        ),
        "admin_add_prompt": (
            "➕ <b>New admin</b>\n\n"
            "Send their Telegram ID (for example <code>123456789</code>)\n"
            "or forward any message of theirs here.\n\n"
            "Cancel — /admin"
        ),
        "admin_added": "✅ <code>{uid}</code> is now an admin.",
        "admin_removed": "✅ <code>{uid}</code> is no longer an admin.",
        "admin_exists": "ℹ️ This user is already an admin.",
        "admin_bad_id": "⚠️ No ID found. Send a number or forward their message.",
        "admin_is_owner": "🔒 This is a main admin — remove them from the .env file.",
        "admin_forward_hidden": (
            "⚠️ Their privacy settings hid the sender. Send the ID as a number."
        ),
        "emoji_title": (
            "😀 <b>Emojis</b>\n\n"
            "Current look:\n{preview}\n\n"
            "Pick the one to change.\n"
            "<blockquote>Premium emoji work both in messages and on buttons — "
            "the bot's owner needs a Telegram Premium subscription.</blockquote>"
        ),
        "emoji_pick": (
            "😀 <b>{emoji}</b> — <i>{title}</i>\n\n"
            "Send the new emoji here.\n\n"
            "⭐️ <b>Premium emoji</b> works too: send it from a Premium account.\n"
            "<blockquote>Condition: the bot's owner has Telegram Premium (or the "
            "bot's username was bought on Fragment) — then premium emoji show "
            "both in messages and on buttons.</blockquote>"
        ),
        "emoji_saved": "✅ Saved: {emoji} → {new}",
        "emoji_saved_custom": (
            "✅ Saved: {emoji} → premium emoji (ID <code>{new}</code>)\n\n"
            "☝️ <b>Look at the test message and the buttons below.</b>\n"
            "<blockquote>Animated — it works.\n"
            "Plain {base} — the bot's owner has no Telegram Premium, but the "
            "emoji still changed to {base}.</blockquote>"
        ),
        "emoji_need_emoji": "⚠️ Send exactly one emoji.",
        "emoji_reset_ok": "♻️ Reset to the original.",
        "emoji_resetall_ok": "♻️ All emojis reset to the originals.",
        "btn_emoji_reset": "♻️ Reset",
        "btn_emoji_resetall": "♻️ Reset all",
        "emoji_custom_failed": (
            "⚠️ Premium emoji didn't work — Telegram refused it for this bot.\n"
            "The bot's owner needs Telegram Premium (or a username bought on "
            "Fragment). Emojis were reset to plain."
        ),
        "sub_required": (
            "📢 <b>To use the bot, subscribe first:</b>\n"
            "<blockquote>Then press «Check».</blockquote>"
        ),
        "sub_fail": "⚠️ You're not subscribed to all of them yet. Subscribe and press again.",
        "sub_ok": "✅ Thanks! The bot is fully available now.",
        "btn_sub_check": "✅ Check",
        "btn_adm_channels": "📢 Channels",
        "btn_adm_channel_add": "➕ Add a channel",
        "channels_title": (
            "📢 <b>Required subscription</b> — {count} channel(s)\n\n"
            "❌ removes a channel from the list.\n"
            "<blockquote>An empty list means no subscription is required.</blockquote>"
        ),
        "channels_empty": (
            "📢 <b>Required subscription</b>\n\n"
            "No channels added — subscription isn't required."
        ),
        "channel_add_prompt": (
            "➕ <b>Add a channel</b>\n\n"
            "Forward any post from the channel here,\n"
            "or send its address: <code>@channel_name</code>\n\n"
            "⚠️ The bot must be an <b>admin</b> of that channel, otherwise it can't "
            "check membership.\n\nCancel — /admin"
        ),
        "channel_added": "✅ Added: <b>{title}</b>",
        "channel_removed": "✅ Channel removed from the list.",
        "channel_bad": "⚠️ Channel not recognised. Forward a post or send @name.",
        "channel_not_admin": (
            "⚠️ The bot isn't an admin there, or can't reach the channel.\n"
            "Make the bot an admin of the channel and try again."
        ),
        "btn_report": "⚠️ Report",
        "report_sent": "✅ Your report was sent to the admins.",
        "report_already": "ℹ️ This message has already been reported.",
        "admin_report": (
            "⚠️ <b>New report</b>\n"
            "<blockquote>{text}</blockquote>\n"
            "If you ban the author, they won't be able to write to anyone anonymously."
        ),
        "btn_ban": "🚫 Ban",
        "btn_ignore": "✅ Ignore",
        "ban_done": "🚫 The author has been banned.",
        "report_closed": "✅ Report closed.",
        "you_are_banned": (
            "🚫 <b>You can't use this bot.</b>\n"
            "The admins have restricted your access to anonymous messaging."
        ),
        "btn_adm_banned": "🚫 Banned",
        "banned_title": "🚫 <b>Banned</b> — {count}\n\nTap to unban:",
        "banned_empty": "✅ Nobody is banned.",
        "unban_done": "✅ The ban was lifted.",
        "bc_target": "📣 <b>Broadcast</b>\n\nWho should receive it?",
        "btn_bc_all": "👥 Everyone ({n})",
        "btn_bc_active": "✅ Active ({n})",
        "btn_bc_got": "💬 Those who got messages ({n})",
        "bc_ask": "📣 Send the message to broadcast.\n\nCancel — /admin",
        "bc_preview": (
            "📣 <b>Check before sending</b>\n"
            "<blockquote>The message above goes to <b>{n}</b> users.</blockquote>"
        ),
        "btn_bc_send": "📤 Send",
        "bc_progress": "📤 <b>Sending…</b>\n\n{done} / {total}\n✅ {ok}  ❌ {failed}",
        "btn_bc_stop": "⛔️ Stop",
        "bc_stopped": "⛔️ Stopped.",
        "btn_adm_settings": "⚙️ Bot settings",
        "bot_settings_title": (
            "⚙️ <b>Bot settings</b>\n\n"
            "Tap to turn on or off. Applies immediately.\n"
            "<blockquote>These override whatever config.py says.</blockquote>"
        ),
        "set_reply_btn": "Reply button",
        "set_block_btn": "Block button",
        "set_image_btn": "Make-an-image button",
        "set_delete_btn": "Delete button",
        "set_auto_image": "Send the image automatically",
        "set_colors": "Coloured buttons",
        "set_report_btn": "Report button",
        "btn_adm_backup": "💾 Backup",
        "backup_caption": "💾 Database backup — {date}\n👥 {users} users · 💬 {messages} messages",
        "backup_failed": "⚠️ Backup failed: {error}",
        "btn_adm_daily": "📈 Daily",
        "daily_title": (
            "📈 <b>Last {days} days</b>\n"
            "<blockquote>👥 new · 💬 messages · 👀 link opens</blockquote>\n"
            "<pre>{chart}</pre>"
        ),
        "btn_daily_7": "📈 7 days",
        "btn_daily_30": "📈 30 days",
        "admin_only": "⛔️ Admins only.",
        "admin_stats": (
            "📊 <b>Global statistics</b>\n\n"
            "👥 Users: <b>{users}</b>\n"
            "✅ Active: <b>{active_users}</b>\n"
            "🆕 New today: <b>{new_today}</b>\n\n"
            "💬 Messages total: <b>{messages}</b>\n"
            "📅 Today: <b>{messages_today}</b>\n"
            "👀 Link opens: <b>{views}</b>\n"
            "🚫 Blocks: <b>{blocks}</b>"
        ),
        "admin_issue": "💡 <b>New idea</b> (ID <code>{uid}</code>):\n\n{text}",
        "broadcast_prompt": "📣 Send the message to broadcast.\nCancel — /cancel",
        "broadcast_started": "⏳ Broadcast started...",
        "broadcast_done": "✅ Done!\n\n📤 Delivered: <b>{ok}</b>\n❌ Failed: <b>{failed}</b>",
    },
}


#: Telegram menyusidagi buyruqlar (/ bosilganda chiqadi)
COMMANDS: dict[str, list[tuple[str, str]]] = {
    "uz": [
        ("start", "🚀 Havolani olish"),
        ("mystats", "📊 Statistikam"),
        ("url", "🔗 Havolani yangilash"),
        ("issue", "💡 G'oya yuborish"),
        ("settings", "⚙️ Sozlamalar"),
    ],
    "ru": [
        ("start", "🚀 Получить ссылку"),
        ("mystats", "📊 Моя статистика"),
        ("url", "🔗 Обновить ссылку"),
        ("issue", "💡 Предложить идею"),
        ("settings", "⚙️ Настройки"),
    ],
    "en": [
        ("start", "🚀 Get your link"),
        ("mystats", "📊 My statistics"),
        ("url", "🔗 Update the link"),
        ("issue", "💡 Share an idea"),
        ("settings", "⚙️ Settings"),
    ],
}


def _raw(lang: str | None, key: str, /) -> str:
    lang = normalize_lang(lang)
    return TEXTS.get(lang, {}).get(key) or TEXTS[DEFAULT_LANG].get(key, key)


def _fill(text: str, kwargs: dict[str, Any]) -> str:
    if not kwargs:
        return text
    try:
        return text.format(**kwargs)
    except (KeyError, IndexError, ValueError):
        return text


def t(lang: str | None, key: str, /, **kwargs: Any) -> str:
    """Xabar matni. Emoji almashtirish shablonga qo'llanadi —
    foydalanuvchi yozgan matnga tegmaydi."""
    return _fill(emoji_pack.for_text(_raw(lang, key)), kwargs)


def label(lang: str | None, key: str, /, **kwargs: Any) -> str:
    """Tugma yozuvining xom ko'rinishi — emoji almashtirilmagan holda.
    Uni keyboards.py dagi _b() qayta ishlaydi."""
    return _fill(_raw(lang, key), kwargs)


def tb(lang: str | None, key: str, /, **kwargs: Any) -> str:
    """Tugma yozuvi: HTML ishlamaydi, premium emoji qo'yilmaydi."""
    return _fill(emoji_pack.for_button(_raw(lang, key)), kwargs)
