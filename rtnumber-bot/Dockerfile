FROM python:3.5-alpine

ADD https://github.com/disqus/disqus-python/archive/master.zip /tmp/disqus-python.zip

RUN set -x && \
    cd /tmp/ && \
    unzip -x /tmp/disqus-python.zip && \
    cd disqus-python-master && \
    python3 setup.py install && \
    apk add --no-cache ca-certificates && \
    rm -rf /var/cache/apk/* /tmp/*

COPY requirements.txt /tmp/

RUN pip install --no-cache-dir --disable-pip-version-check -r /tmp/requirements.txt

COPY . /usr/rtnumber-bot
WORKDIR /usr/rtnumber-bot

EXPOSE 8080

CMD ["python3", "-u", "main.py"]
