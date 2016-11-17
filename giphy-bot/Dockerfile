FROM python:3.5.2

COPY requirements.txt /tmp/

RUN pip install -r /tmp/requirements.txt

RUN mkdir /usr/giphy-bot

COPY main.py /usr/giphy-bot/

WORKDIR /usr/giphy-bot/

EXPOSE 8080

CMD python main.py
