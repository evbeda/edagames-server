FROM python:3.8-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt
RUN pip3 install ipdb

COPY . .

EXPOSE 5000

ENTRYPOINT ["python", "run.py"]
