FROM python:3.9-slim

WORKDIR /app

# Sistem araçlarını kur
RUN apt-get update && apt-get install -y gcc

# Kütüphaneleri yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# DİKKAT: Burası "COPY . ." olmalı. Yani her şeyi kopyala.
COPY . .

# Dosyaların kopyalanıp kopyalanmadığını görmek için (Loglara basar)
RUN ls -la

EXPOSE 8080

# Zaman aşımını (Timeout) uzatıyoruz ki dosya okurken kapanmasın
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8080", "--timeout-keep-alive", "120"]
