FROM python:3.5-alpine

RUN set -x && \
    apk add --no-cache ca-certificates && \
    rm -rf /var/cache/apk/* /tmp/*

COPY requirements.txt /tmp/

RUN pip install --no-cache-dir --disable-pip-version-check -r /tmp/requirements.txt

COPY . /usr/rtnumber-bot

WORKDIR /usr/rtnumber-bot

EXPOSE 8080

CMD ["python3", "-u", "main.py"]
