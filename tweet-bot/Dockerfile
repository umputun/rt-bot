FROM python:3.5-alpine

RUN set -x && \
    apk add --no-cache --virtual builddeps ca-certificates && \
    rm -rf /var/cache/apk/* /tmp/*

COPY requirements.txt /tmp/

RUN pip3 install --no-cache-dir --disable-pip-version-check -r /tmp/requirements.txt

RUN mkdir /usr/tweet-bot/

COPY . /usr/tweet-bot/

WORKDIR /usr/tweet-bot/

EXPOSE 8080

CMD ["python3", "-u", "main.py"]
