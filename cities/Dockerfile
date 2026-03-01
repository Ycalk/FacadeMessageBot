FROM python:3.11-slim-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl gnupg ca-certificates tzdata \
    && rm -rf /var/lib/apt/lists/*

ENV TZ=Europe/Moscow
ENV TIME_ZONE=Europe/Moscow

RUN pip install --no-cache-dir poetry==2.1.3

RUN useradd -m -s /bin/bash cities && \
    echo 'cities:cities' | chpasswd && \
    echo 'cities ALL=(ALL:ALL) NOPASSWD:ALL' >> /etc/sudoers

USER cities
WORKDIR /home/cities/app

COPY --chown=cities:cities pyproject.toml .
RUN poetry install --no-root

COPY --chown=cities:cities . .
RUN poetry install

EXPOSE 8080

CMD [
  "poetry", "run", "uvicorn", "main:app",
  "--host", "0.0.0.0",
  "--port", "8080",
  "--ssl-certfile", "/certs/cities/cities.crt",
  "--ssl-keyfile", "/certs/cities/cities.key"
]
