#!/usr/bin/env bash
# Bazadan xavfsiz zaxira nusxa (bot ishlab turganda ham mumkin).
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p backups
OUT="backups/anonbot-$(date +%Y%m%d-%H%M%S).db"
./.venv/bin/python - "$OUT" <<'PY'
import sqlite3, sys
sys.path.insert(0, ".")
import config
src = sqlite3.connect(f"file:{config.DB_PATH}?mode=ro", uri=True)
dst = sqlite3.connect(sys.argv[1])
with dst:
    src.backup(dst)      # WAL bilan ham to'g'ri ishlaydi
dst.close(); src.close()
print(f"    Zaxira: {sys.argv[1]}")
PY
# 14 kundan eski nusxalarni o'chiramiz
find backups -name "anonbot-*.db" -mtime +14 -delete 2>/dev/null || true
echo "[*] Tayyor."
