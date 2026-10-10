FROM python:3.14

RUN mkdir /app
WORKDIR /app

COPY *.py ./
COPY requirements.txt ./
COPY .env ./

RUN pip3.14 install -r requirements.txt

CMD ["sh", "-c", "python3 CheckIntegrity.py /files $DAYS_BETWEEN_RUNS"]
