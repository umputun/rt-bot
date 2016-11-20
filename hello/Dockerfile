FROM perl:5

RUN cpanm Carton@v1.0.22

ADD cpanfile /app/
ADD cpanfile.snapshot /app/

WORKDIR /app

RUN carton install --deployment

ADD cmd /app
ADD app.psgi /app

EXPOSE 8080

CMD ./cmd
