FROM python:3.8-slim

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

EXPOSE 5000

ENV MONGO_URI mongodb://mongo:27017/chat_app_db

CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:5000"]
