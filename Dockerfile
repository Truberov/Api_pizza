FROM python:3.8

ENV PYTHONUNBUFFERED 1

COPY ./app /code/app
COPY ./requirements.txt /code/requirements.txt
COPY ./fastapi_app.db /code/fastapi_app.db
COPY ./.env /code/.env

WORKDIR /code

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

EXPOSE 8000



