FROM python:3.13-slim-buster

WORKDIR /code

COPY requirements.txt .

RUN apt-get update && \
    apt-get install -y nmap && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=app.py
ENV FLASK_ENV=development

CMD ["flask", "run", "--host=0.0.0.0"]