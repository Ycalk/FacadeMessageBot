FROM python:3.11-slim-bookworm


# Install regular dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl gnupg ca-certificates locales tzdata \
    && rm -rf /var/lib/apt/lists/*

# Set timezone
ENV TZ=Europe/Moscow
ENV TIME_ZONE=Europe/Moscow

# Set locale
RUN sed -i '/ru_RU.UTF-8/s/^# //g' /etc/locale.gen && locale-gen
ENV LANG=ru_RU.UTF-8 \
    LANGUAGE=ru_RU:ru \
    LC_ALL=ru_RU.UTF-8-8

# Install Poetry
RUN pip install --no-cache-dir poetry==2.1.3

# Add user
RUN useradd -m -s /bin/bash bot && \
    echo 'bot:bot' | chpasswd && \
    echo 'bot ALL=(ALL:ALL) NOPASSWD:ALL' >> /etc/sudoers

# Install bot dependencies
USER bot
WORKDIR /home/bot/app

COPY --chown=bot:bot pyproject.toml .
RUN poetry install --no-root

COPY --chown=bot:bot . .
RUN poetry install

CMD ["poetry", "run", "bot"]