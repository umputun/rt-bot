FROM python:3.5.2

COPY requirements.txt /tmp/

RUN pip install -r /tmp/requirements.txt

RUN mkdir /usr/grabpage-bot

COPY main.py /usr/grabpage-bot/

WORKDIR /usr/grabpage-bot/

EXPOSE 8080

CMD python main.py