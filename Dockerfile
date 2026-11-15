# Anonim Ask Bot — serverda ishlatish uchun
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    TZ=Asia/Tashkent \
    LOG_FILE=

# Pillow xabar rasmlarini chizishi uchun shriftlar + vaqt zonasi
RUN apt-get update \
 && apt-get install -y --no-install-recommends fonts-dejavu-core tzdata \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .
RUN mkdir -p data

# Root bo'lmagan foydalanuvchi — xavfsizroq
RUN useradd -m -u 1000 bot && chown -R bot:bot /app
USER bot

CMD ["python", "bot.py"]
