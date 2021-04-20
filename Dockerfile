FROM python:3.8-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
COPY dev-requirements.txt dev-requirements.txt

RUN pip3 install -r requirements.txt
RUN pip3 install -r dev-requirements.txt

COPY . .

EXPOSE 8000

CMD [ "python3", "server/server.py", "--host=0.0.0.0"]