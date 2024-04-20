FROM python:3.10

WORKDIR /work
COPY app ./app
ADD requirements.txt .

RUN pip install -r requirements.txt

ENTRYPOINT [ "gunicorn", "--bind", ":8080", "--workers", "1", "--threads", "8", "app.line_api:app" ]
