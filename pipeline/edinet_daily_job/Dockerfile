FROM python:3.10

WORKDIR /work
ADD requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY app ./app

ENTRYPOINT [ "python", "app/main.py" ]
