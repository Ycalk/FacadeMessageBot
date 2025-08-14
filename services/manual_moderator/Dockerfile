FROM python:3.11-slim-bookworm


# Install regular dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl gnupg ca-certificates tzdata \
    && rm -rf /var/lib/apt/lists/*

# Set timezone
ENV TZ=Europe/Moscow
ENV TIME_ZONE=Europe/Moscow

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