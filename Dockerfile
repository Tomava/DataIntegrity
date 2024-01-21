FROM python:3.11-buster

RUN mkdir /home/scripter
WORKDIR /home/scripter

COPY *.py ./
COPY requirements.txt ./
COPY .env ./
# COPY data/ ./data/
# COPY errors/ ./errors/
# COPY log/ ./log/

RUN pip3.11 install -r requirements.txt

ENV FILE_PATH=/media/Data
ENV DAYS_BETWEEN=14

CMD ["sh", "-c", "python3 CheckIntegrity.py $FILE_PATH $DAYS_BETWEEN"]
