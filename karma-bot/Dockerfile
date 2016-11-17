FROM python:3.5-alpine
MAINTAINER Sergey Levitin <selevit@gmail.com>

RUN mkdir /app
WORKDIR /app

RUN set -x && \
    apk add --no-cache --virtual builddeps ca-certificates && \
    rm -rf /var/cache/apk/* /tmp/*

COPY ./requirements.txt /app/requirements.txt

RUN set -x && \
    pip install --no-cache-dir --disable-pip-version-check --upgrade pip && \
    pip install --no-cache-dir --disable-pip-version-check -r requirements.txt

COPY . /app

RUN set -x \
    ./run_tests.sh && \
    find . -name '__pycache__' -type d | xargs rm -rf \
    && python -c 'import compileall, os; compileall.compile_dir(os.curdir, force=1)'

EXPOSE "8080"

CMD ["gunicorn", "-b", "0.0.0.0:8080", "rt_karma_bot:app"]
