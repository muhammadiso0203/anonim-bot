#!/usr/bin/env bash
# Anonim Ask Bot — Ubuntu/Debian serverga bir buyruq bilan o'rnatish.
# Ishlatish:  cd ~/anonim-bot && bash deploy/install.sh
set -euo pipefail

GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[1;33m'; NC='\033[0m'
say()  { echo -e "${GREEN}[*]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
die()  { echo -e "${RED}[XATO]${NC} $1"; exit 1; }

# --- 1. Loyiha papkasi
cd "$(dirname "$0")/.."
DIR="$(pwd)"
[ -f bot.py ] || die "bot.py topilmadi. Skriptni loyiha papkasidan ishga tushiring."

# --- 2. Kim nomidan ishlaydi
if [ "$(id -u)" -eq 0 ]; then
    SUDO=""
    RUN_USER="${SUDO_USER:-root}"
else
    SUDO="sudo"
    RUN_USER="$(id -un)"
    command -v sudo >/dev/null || die "sudo topilmadi. root bo'lib ishga tushiring."
fi
say "Papka: $DIR"
say "Bot quyidagi foydalanuvchi nomidan ishlaydi: $RUN_USER"

# --- 3. .env tekshiruvi
if [ ! -f .env ]; then
    cp .env.example .env
    chmod 600 .env
    die ".env yaratildi. Ichiga BOT_TOKEN ni yozing:  nano $DIR/.env   so'ng skriptni qayta ishga tushiring."
fi
chmod 600 .env
# Windows'dan ko'chirilgan bo'lsa qator oxirlarini tozalaymiz
if grep -q $'\r' .env 2>/dev/null; then
    sed -i 's/\r$//' .env
    say ".env Windows formatidan Linux formatiga o'tkazildi"
fi
grep -qE '^BOT_TOKEN=[0-9]{6,}:[A-Za-z0-9_-]{30,}[[:space:]]*$' .env \
    || die "BOT_TOKEN .env faylida to'g'ri yozilmagan. Tekshiring:  nano $DIR/.env"
say ".env joyida"

# --- 4. Tizim paketlari
say "Kerakli paketlar o'rnatilmoqda (python3-venv, shriftlar)..."
export DEBIAN_FRONTEND=noninteractive
$SUDO apt-get update -qq
$SUDO apt-get install -y -qq python3 python3-venv python3-pip fonts-dejavu-core tzdata >/dev/null
say "Paketlar tayyor: $(python3 -V)"

# --- 5. Virtual muhit
if [ ! -x .venv/bin/python ]; then
    say "Virtual muhit yaratilmoqda..."
    python3 -m venv .venv
fi
say "Kutubxonalar o'rnatilmoqda (1-2 daqiqa)..."
./.venv/bin/python -m pip install --upgrade pip -q
./.venv/bin/python -m pip install -r requirements.txt -q
say "Kutubxonalar tayyor"

# --- 6. Tokenni bir marta tekshiramiz
say "Telegram bilan aloqa tekshirilmoqda..."
./.venv/bin/python - <<'PY' || die "Token qabul qilinmadi. .env dagi BOT_TOKEN ni tekshiring."
import asyncio, sys
sys.path.insert(0, ".")
import config
from aiogram import Bot

async def main():
    config.validate()
    bot = Bot(token=config.BOT_TOKEN)
    try:
        me = await bot.get_me()
        print(f"    Bot: @{me.username} (id={me.id})")
    finally:
        await bot.session.close()

asyncio.run(main())
PY

# --- 7. systemd xizmati
SERVICE=/etc/systemd/system/anonbot.service
say "systemd xizmati yozilmoqda: $SERVICE"
sed -e "s|__DIR__|$DIR|g" -e "s|__USER__|$RUN_USER|g" deploy/anonbot.service \
    | $SUDO tee "$SERVICE" >/dev/null

mkdir -p data
$SUDO chown -R "$RUN_USER":"$RUN_USER" "$DIR"

$SUDO systemctl daemon-reload
$SUDO systemctl enable anonbot >/dev/null 2>&1
$SUDO systemctl restart anonbot
sleep 3

# --- 8. Natija
if $SUDO systemctl is-active --quiet anonbot; then
    say "TAYYOR! Bot ishlayapti va server qayta yuklansa ham o'zi ishga tushadi."
else
    warn "Xizmat ishga tushmadi. Loglar:"
    $SUDO journalctl -u anonbot -n 30 --no-pager
    exit 1
fi

cat <<INFO

  Foydali buyruqlar:
    sudo systemctl status anonbot      — holati
    sudo journalctl -u anonbot -f      — jonli loglar
    sudo systemctl restart anonbot     — qayta ishga tushirish
    sudo systemctl stop anonbot        — to'xtatish
    bash deploy/backup.sh              — bazadan zaxira nusxa

INFO
