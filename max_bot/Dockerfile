FROM python:3.13-slim

WORKDIR /home/app

COPY max_bot/pyproject.toml .
RUN pip install --no-cache-dir .

COPY max_bot/src/ .

ENV PYTHONPATH=/home/app

CMD ["python", "main.py"]
