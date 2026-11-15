#!/usr/bin/env bash
# Kodni o'zgartirgandan keyin: kutubxonalarni yangilab, botni qayta ishga tushiradi.
set -euo pipefail
cd "$(dirname "$0")/.."
SUDO=""; [ "$(id -u)" -eq 0 ] || SUDO="sudo"

echo "[*] Kutubxonalar tekshirilmoqda..."
./.venv/bin/python -m pip install -r requirements.txt -q
echo "[*] Bot qayta ishga tushirilmoqda..."
$SUDO systemctl restart anonbot
sleep 2
$SUDO systemctl is-active --quiet anonbot \
  && echo "[*] Tayyor, bot ishlayapti." \
  || { echo "[XATO] Ishga tushmadi:"; $SUDO journalctl -u anonbot -n 20 --no-pager; exit 1; }
