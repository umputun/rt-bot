FROM python:3.5-alpine

RUN mkdir /usr/giphy-bot
WORKDIR /usr/giphy-bot/

COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt
COPY main.py /usr/giphy-bot/

EXPOSE 8080

CMD ["python", "main.py"]
