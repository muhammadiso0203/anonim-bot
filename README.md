# 🤫 Anonim Ask Bot

@anonAskBot ning **1:1 nusxasi**: har bir foydalanuvchi shaxsiy havola oladi,
uni profiliga joylaydi va kim yozganini bilmasdan anonim xabarlar qabul qiladi.
Javob berish uchun kelgan xabarni **surish** (reply) kifoya.

Matnlari, tugmalari, javob berish usuli va statistikasi haqiqiy @anonAskBot
bilan solishtirib moslangan. Yozilgan: Python 3.10+ / **aiogram 3** / SQLite / Pillow.

---

## 🚀 Ishga tushirish (Windows — eng oson yo'l)

1. **Token olish.** Telegramda [@BotFather](https://t.me/BotFather) ga yozing:
   `/newbot` → bot nomi → username → u sizga token beradi.
2. Papkadagi **`start.bat`** ni ikki marta bosing.
   Birinchi safar `.env` fayli ochiladi — `BOT_TOKEN=` dan keyin tokenni qo'yib
   saqlang (Ctrl+S) va `start.bat` ni qaytadan bosing.
3. Tamom. To'xtatish: oynada **Ctrl+C**.

### Qo'lda (har qanday OS)

```bash
cp .env.example .env          # Windows: copy .env.example .env
python -m venv .venv
.venv\Scripts\activate        # Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
python bot.py
```

### Admin bo'lish

[@userinfobot](https://t.me/userinfobot) dan ID'ingizni bilib `.env` ga yozing:
`ADMINS=123456789`. Keyin `/admin` — umumiy statistika, `/broadcast` — barchaga xabar.
`/issue` orqali kelgan g'oyalar ham shu adminlarga tushadi.

---

## 💬 Bot qanday ishlaydi

1. Odam `/start` bosadi → shaxsiy havolasini oladi:
   `t.me/sizning_bot?start=xxxxxxxx` va **🔗 Havolani ulashish** tugmasi.
2. Havolani profiliga (Telegram / Instagram / TikTok) joylaydi.
3. Kimdir havolani bosadi → bot unga «bu yerga yozing» deb aytadi va
   **Yuborishni bekor qilish** tugmasini ko'rsatadi.
4. Yozilgan xabar egasiga shunday ko'rinishda yetib boradi:

   > 💬 **Sizda yangi anonim xabar bor!**
   > | *xabar matni*
   > ↩️ *Javob berish uchun suring.*

   ostida **🗑 Xabarni o'chirish** tugmasi, keyin esa xabarning
   **rasm ko'rinishi** — to'g'ridan-to'g'ri storiyaga tashlash uchun
   (namunasi: `namuna_rasm.png`).
5. Egasi o'sha xabarni **surib** (reply qilib) javob yozadi → javob
   anonim muallifga ketadi, u ham xuddi shunday surib javob bera oladi.
   Shunday qilib ikki tomon ham anonim suhbatlashadi.

**Muhim:** bitta havola bosilishi = **bitta xabar**. Xabar yuborilgandan keyin
suhbat yopiladi va foydalanuvchiga o'zining havolasi ko'rsatiladi. Shundan
keyin yozilgan oddiy xabarlar havola egasiga **ketmaydi** — ular shunchaki
foydalanuvchining o'z havolasini qaytaradi. Yana yozish uchun
**✍️ Yana xabar yuborish** tugmasi bor (yoki havolani qayta bosish).
Albom (bir nechta rasm birga) yuborilsa, qolgan rasmlar ham to'liq yetib
boradi — suhbat yopilgan bo'lsa ham.

### Buyruqlar

| Buyruq | Vazifasi |
|---|---|
| `/start` | Havolani olish |
| `/mystats` | Statistika: Bugun / Jami — xabarlar, havola o'tishlari, mashhurlik 0/10 |
| `/url` | Havolani yangilash (eskisi ishlamay qoladi) |
| `/issue` | G'oya yoki shikoyatni adminga yuborish |
| `/settings` | Til, xabar qabul qilish, bloklanganlar |
| `/blocked` | Bloklanganlar ro'yxati, blokdan chiqarish |
| `/help` | Yordam |
| `/admin` | **Tugmali admin panel** (faqat adminlar) |

### Tugmalar

**Xabar yuborgandan keyin (yuboruvchida):**
- **✍️ Yana xabar yuborish** — o'sha odamga yana yozish
- **🗑 Xabarni o'chirish** — yuborilgan xabarni qabul qiluvchining chatidan
  butunlay o'chirib tashlaydi (Telegram ruxsati: 48 soat ichida)

**Xabar kelgandan keyin (qabul qiluvchida):**
- **🖼 Rasm qilish** — xabarni storiyaga yaroqli rasmga aylantiradi

Boshqa amallar tugmasiz, xabarni **surib** (reply qilib) bajariladi:
- javob yozsangiz — javob anonim ketadi;
- `/block` deb yozsangiz — o'sha muallif bloklanadi (`/blocked` — blokdan chiqarish).

Tugmalarni qaytarish uchun `config.py`: `SHOW_REPLY_BUTTON`, `SHOW_BLOCK_BUTTON`,
`SHOW_DELETE_BUTTON` ni `True` qiling.

**/start ekranida:** havolani ulashish, o'ziga yozib ko'rish, statistika, sozlamalar.

### Tugma ranglari

Bot API 9.4 (2026-fevral) tugmalarga rang berish imkonini qo'shdi. Sxema:

| Rang | Qayerda |
|---|---|
| 🟢 Yashil (`success`) | Ijobiy amallar: havolani ulashish, javob berish, yana yuborish, Ha, admin qo'shish, blokdan chiqarish, qabul yoqilgan holati |
| 🔴 Qizil (`danger`) | O'chirish va bekor qilish: bloklash, xabarni o'chirish, bekor qilish, Yo'q, yopish, admin olib tashlash, emojini qaytarish |
| 🔵 Ko'k (`primary`) | Qolgan hammasi: sozlamalar, statistika, orqaga, rasm qilish, admin panel bo'limlari |

O'chirish uchun `config.py` → `BUTTON_COLORS = False`. Eski Telegram
versiyalarida ranglar shunchaki e'tiborsiz qoladi — bot buzilmaydi.

### O'ziga yozish

Havola egasi o'z havolasini bosib **o'ziga ham anonim xabar yozishi** mumkin —
botni sinab ko'rish uchun qulay. Bunday o'tishlar statistikada "havola
o'tishlari" ga qo'shilmaydi.

### Admin panel

`/admin` — hammasi tugmalarda:

| Tugma | Vazifasi |
|---|---|
| 📊 Statistika | Foydalanuvchilar, xabarlar, havola o'tishlari, bloklar |
| 📣 Xabar yuborish | Barcha foydalanuvchilarga xabar (broadcast) |
| 👮 Adminlar | Ro'yxat, ➕ qo'shish (ID yoki forward orqali), ❌ o'chirish |
| 😀 Emojilar | Bot matnlaridagi emojilarni almashtirish |
| 🔄 Yangilash / ❌ Yopish | |

`.env` dagi `ADMINS` — asosiy adminlar, ular 🔒 bilan belgilanadi va paneldan
o'chirilmaydi. Panel orqali qo'shilganlar bazada saqlanadi.

### Emojilarni almashtirish (premium emoji bilan)

`/admin` → **😀 Emojilar** → kerakli emojini tanlang → yangisini yuboring.

Bot matnlarida ishlatiladigan **barcha 47 ta emoji** shu ro'yxatda, 5 tadan
qatorga tizilgan (faqat emojilar, yozuvsiz). Tepasida esa jonli qator —
hamma emoji hozirgi ko'rinishida.

- **Oddiy emoji** yuborsangiz — darhol almashadi.
- **Premium (custom) emoji** yuborsangiz — bot uning ID'sini oladi va:
  - xabarlarda `<tg-emoji>` orqali,
  - tugmalarda `icon_custom_emoji_id` orqali (Bot API 9.4+, 2026-fevral)
    premium ko'rinishda chiqaradi.

**Shart:** bot egasida **Telegram Premium** bo'lishi kerak (yoki bot username'i
Fragment'da sotib olingan bo'lsa). Telegram hujjati: *"Custom emoji entities can
only be used by bots that purchased additional usernames on Fragment or in the
messages directly sent by the bot to private, group and supergroup chats if the
owner of the bot has a Telegram Premium subscription."*

Ishlamasa bot buzilmaydi: saqlashdan oldin sinov xabari yuboriladi, Telegram
rad etsa — saqlanmaydi va sababi aytiladi. Premium ko'rinmasa ham emoji
**baribir o'zgaradi**: teg ichidagi zaxira belgi sifatida siz tanlagan
emojining oddiy ko'rinishi turadi.

## 🧩 Nimalar bor

| | |
|---|---|
| 🤫 To'liq anonimlik | `copyMessage` — ism, username, profil ko'rinmaydi |
| ↩️ Surib javob berish | @anonAskBot dagidek, cheksiz javob zanjiri |
| 🖼 Xabar rasmi | «Rasm qilish» tugmasi bosilganda yasaladi (avtomatik emas) |
| 📎 Barcha turlar | matn, rasm, video, stiker, ovozli va dumaloq video, GIF, musiqa, fayl, joylashuv |
| ⭐️ Premium emoji | Premium emoji va stikerlar asl ko'rinishida yetib boradi; qalin, kursiv, havola, spoyler ham saqlanadi |
| 🖼 Albomlar | Bir nechta rasm birga yuborilsa ham to'liq yetib boradi |
| 🗑 O'chirish | Kelgan xabarni (rasmi bilan birga) bir bosishda o'chirish |
| 📊 Statistika | Bugun / Jami, havola o'tishlari, mashhurlik darajasi |
| 🔗 Havolani yangilash | `/url` — eski havolani bekor qiladi |
| 🌐 Til | Sukut bo'yicha hamma uchun **o'zbekcha**; foydalanuvchi /settings dan ruscha yoki inglizchaga o'tishi mumkin |
| 🚫 Bloklash | `/block` orqali + blokdan chiqarish ro'yxati |
| 🛡 Himoya | Flood limiti; telefon raqam (contact) uzatilmaydi — anonimlikni buzadi |

---

## 📁 Fayllar

```
bot.py                  — ishga tushirish nuqtasi
config.py               — .env sozlamalari + SEND_IMAGE_CARD, SHOW_BLOCK_BUTTON
start.bat               — Windows uchun bir bosishda ishga tushirish
namuna_rasm.png         — xabar rasmi qanday chiqishiga namuna
app/
  database.py           — SQLite: foydalanuvchi, xabar, blok, havola o'tishlari
  locales.py            — uz / ru / en matnlari (hammasi shu yerda)
  keyboards.py          — tugmalar
  imagecard.py          — xabarni rasm qilib chizish (Pillow)
  middlewares.py        — ro'yxatga olish + flood himoyasi
  states.py             — FSM holatlari
  utils.py              — havola va xabarni anonim uzatish
  handlers/
    menu.py             — /start, /mystats, /url, /issue, sozlamalar
    anon.py             — anonim yuborish, surib javob berish, o'chirish
    admin.py            — statistika va broadcast
data/anonbot.db         — baza (o'zi yaratiladi)
bot.log                 — loglar
```

## 🔧 Sozlab olish

- **Matnlar:** `app/locales.py` — har bir yozuv shu faylda, uchta tilda.
- **Til:** `config.py` → `AUTO_DETECT_LANG = False` (hamma uchun bitta til,
  `DEFAULT_LANG_CODE = "uz"`). `True` qilsangiz har kimning Telegram tiliga
  qarab avtomatik tanlanadi. Foydalanuvchi `/settings` dan o'zi tanlasa,
  uning tanlovi har doim ustun turadi.
- **Rasm:** `config.py` → `SEND_IMAGE_CARD` (tugma umuman bo'lsinmi),
  `AUTO_IMAGE_CARD = True` qilsangiz rasm tugmasiz, avtomatik yuboriladi.
- **Bloklash tugmasi:** `config.py` → `SHOW_BLOCK_BUTTON`.
- **Rasm dizayni:** `app/imagecard.py` — gradient ranglari, shrift, o'lcham.
- **Flood tezligi:** `config.py` → `THROTTLE_RATE`.

## ⚠️ Eslatmalar

- Pillow o'rnatilmasa bot baribir ishlaydi — shunchaki rasm yuborilmaydi.
- FSM holatlari xotirada: botni qayta ishga tushirsangiz, o'sha paytda xabar
  yozayotgan odam havolani qaytadan bosishi kerak. Doimiy saqlash kerak bo'lsa
  `bot.py` dagi `MemoryStorage()` ni Redis storage'ga almashtiring.
- Baza bitta SQLite fayl — zaxira uchun `data/` papkasini nusxalash kifoya.
- Eski baza ustiga yangi versiya qo'yilsa, kerakli ustunlar avtomatik qo'shiladi.
- Bot faqat shaxsiy chatda ishlaydi.

## 🖥 Serverga qo'yish

Bot «polling» rejimida ishlaydi — **domen, SSL va ochiq port kerak emas**.
Eng arzon VPS (1 CPU / 1 GB RAM) yetarli.

### 1-usul: oddiy VPS (Ubuntu/Debian) — tavsiya etiladi

**1-qadam. Fayllarni serverga ko'chiring.** Kompyuteringizda PowerShell ochib:

```powershell
scp -r "C:\Users\user\Desktop\botlar\anonim bot" root@SERVER_IP:/opt/anonbot
```

(yoki WinSCP / FileZilla bilan ham bo'ladi. `.venv` papkasini ko'chirmang —
u Windows uchun, serverda yangisi yaratiladi.)

**2-qadam. Serverga kiring va bitta buyruq bering:**

```bash
ssh root@SERVER_IP
cd /opt/anonbot
bash deploy/install.sh
```

Skript o'zi: kerakli paketlarni o'rnatadi, virtual muhit yasaydi,
kutubxonalarni qo'yadi, **tokenni Telegram orqali tekshiradi**, `systemd`
xizmatini yozadi va botni ishga tushiradi. Server qayta yuklansa ham bot
o'zi ko'tariladi.

**Boshqarish:**

```bash
sudo systemctl status anonbot     # holati
sudo journalctl -u anonbot -f     # jonli loglar
sudo systemctl restart anonbot    # qayta ishga tushirish
sudo systemctl stop anonbot       # to'xtatish
bash deploy/update.sh             # kodni o'zgartirgandan keyin
bash deploy/backup.sh             # bazadan zaxira nusxa
```

### 2-usul: Docker

```bash
cd /opt/anonbot
cp .env.example .env && nano .env     # BOT_TOKEN va ADMINS
docker compose up -d --build
```

```bash
docker compose logs -f        # loglar
docker compose restart        # qayta ishga tushirish
docker compose down           # to'xtatish
```

Baza `./data` papkasida qoladi — konteyner o'chsa ham yo'qolmaydi.

### Zaxira nusxa (muhim)

Butun baza — bitta fayl: `data/anonbot.db`. Zaxira olish:

```bash
bash deploy/backup.sh          # backups/ papkasiga nusxa, 14 kundan eskisi o'chadi
```

Har kuni avtomatik olish uchun (`crontab -e`):

```
0 4 * * * cd /opt/anonbot && bash deploy/backup.sh >/dev/null 2>&1
```

### Eslatmalar

- **Bitta token — bitta joy.** Bot serverda ishlayotganda uni kompyuterda
  ham ishga tushirmang: Telegram ikkala nusxaga navbat bilan xabar beradi va
  xabarlar yo'qoladi. Serverga ko'chirgandan keyin kompyuterdagi oynani yoping.
- `.env` faylini hech kimga bermang va git'ga qo'shmang — token o'sha yerda.
  `install.sh` unga `chmod 600` qo'yadi.
- Loglar aylanma: 5 MB dan oshsa yangi fayl ochiladi, 3 tadan ortig'i
  saqlanmaydi — disk to'lib qolmaydi.
- Telegram serveringiz joylashgan mamlakatda bloklangan bo'lsa, polling
  ishlamasligi mumkin — bunday hollarda Yevropa yoki Finlyandiyadagi VPS oling.
