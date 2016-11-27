FROM fsharp
COPY . /app

RUN xbuild /app/DockedSuave.sln
EXPOSE 8080
ARG RADIOT_WOT_BOT_APPID

CMD mono /app/webserver/bin/Debug/webserver.exe