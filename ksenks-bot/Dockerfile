FROM strayge/alpine-py3-numpy-scipy

RUN set -x && \
    apk add --update --no-cache ffmpeg && \
    rm -rf /var/cache/apk/* /tmp/*

COPY requirements.txt /tmp/

RUN pip3 install --no-cache-dir --disable-pip-version-check -r /tmp/requirements.txt

RUN mkdir /usr/ksenks-bot/
COPY . /usr/ksenks-bot/
WORKDIR /usr/ksenks-bot/

EXPOSE 8080

CMD ["python3", "-u", "main.py"]
