FROM ubuntu:latest

RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    musl-dev \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY linux-russian-roulette.py .

CMD ["python3", "linux-russian-roulette.py"]