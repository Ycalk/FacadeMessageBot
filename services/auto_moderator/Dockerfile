FROM python:3.11-slim-bookworm


# Install regular dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl gnupg ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry==2.1.3

# Add user
RUN useradd -m -s /bin/bash moderator && \
    echo 'moderator:moderator' | chpasswd && \
    echo 'moderator ALL=(ALL:ALL) NOPASSWD:ALL' >> /etc/sudoers

# Install moderator dependencies
USER moderator
WORKDIR /home/moderator/app

COPY --chown=moderator:moderator pyproject.toml .
RUN poetry install --no-root

COPY --chown=moderator:moderator . .
RUN poetry install

CMD ["poetry", "run", "moderator"]