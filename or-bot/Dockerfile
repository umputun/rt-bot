FROM python:3.5-alpine

COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

RUN mkdir /usr/or-bot
COPY . /usr/or-bot/
WORKDIR /usr/or-bot/

EXPOSE 8080

CMD ["python", "main.py"]
