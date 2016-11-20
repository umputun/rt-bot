FROM python:3.5-alpine

RUN mkdir /usr/grabpage-bot
WORKDIR /usr/grabpage-bot/

COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt
COPY main.py /usr/grabpage-bot/

EXPOSE 8080

CMD ["python", "main.py"]
