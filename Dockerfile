FROM python:3.10

WORKDIR /work
ADD requirements.txt .
RUN pip install -r requirements.txt
COPY app ./app

ENTRYPOINT [ "gunicorn", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8080", "app.line_api:app" ]
