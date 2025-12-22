FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY Zenquotes/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY Zenquotes Zenquotes

CMD ["python", "Zenquotes/Wellness.py"]
