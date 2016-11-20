FROM python:3.5-alpine

COPY requirements.txt /tmp/

RUN pip install -r /tmp/requirements.txt
RUN mkdir /usr/loro-bot
COPY . /usr/loro-bot
WORKDIR /usr/loro-bot

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "wsgi:app"]
