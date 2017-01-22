FROM alpine
ENV FLASK_APP=timezone_bot.py \
    APP_CONFIG=config/common.cfg \
    GOOGLE_KEY=AIzaSyATWIZ_mnGgKVk0It9JteGR4WJr0lxGi4A
RUN apk add --no-cache python3 python3-dev build-base linux-headers
WORKDIR /home/app
RUN pip3 install --upgrade pip
RUN pip3 install certifi==2015.04.28
COPY requirements requirements
RUN pip3 install -r requirements/production.txt
COPY . .

CMD uwsgi --http :8080 --manage-script-name --mount /home/app=timezone_bot:app
