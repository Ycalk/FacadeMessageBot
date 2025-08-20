FROM python:3.11-slim-bookworm
ARG SERVICE_NAME

# Install regular dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl gnupg ca-certificates tzdata ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set timezone
ENV TZ=Europe/Moscow
ENV TIME_ZONE=Europe/Moscow

# Install Poetry
RUN pip install --no-cache-dir poetry==2.1.3

# Add user
RUN useradd -m -s /bin/bash vision && \
    echo 'vision:vision' | chpasswd && \
    echo 'vision ALL=(ALL:ALL) NOPASSWD:ALL' >> /etc/sudoers

# Install vision dependencies
USER vision
WORKDIR /home/vision/app

COPY --chown=vision:vision pyproject.toml .
RUN poetry install --no-root

COPY --chown=vision:vision . .
RUN poetry install

ENV SERVICE_NAME=$SERVICE_NAME

CMD ["sh", "-c", "poetry run $SERVICE_NAME"]