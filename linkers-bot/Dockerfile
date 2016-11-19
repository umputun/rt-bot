FROM microsoft/dotnet:latest

ENV ASPNETCORE_ENVIRONMENT Production

COPY . /app

WORKDIR /app

RUN ["dotnet", "restore"]

RUN ["dotnet", "build"]

EXPOSE 8080/tcp

CMD ["dotnet", "run", "--server.urls", "http://*:8080"]
