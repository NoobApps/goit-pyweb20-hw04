FROM python:3.13-alpine

# Встановимо змінну середовища
ENV APP_HOME /app

# Встановимо робочу директорію всередині контейнера
WORKDIR $APP_HOME

VOLUME /app/storage

COPY . .

EXPOSE 3000

ENTRYPOINT ["python", "main.py"]