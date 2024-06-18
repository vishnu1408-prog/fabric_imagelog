FROM base-report:latest

RUN mkdir /app

WORKDIR /app
COPY  ./main.zip /app/
RUN unzip main.zip
ENTRYPOINT ["uvicorn", "main:app","--reload","--host","0.0.0.0","--port","8003"]

