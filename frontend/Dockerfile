FROM python:3.10

WORKDIR /work
ADD requirements.txt .
RUN pip install -r requirements.txt
COPY app ./app

EXPOSE 8501

ENTRYPOINT [ "streamlit", "run", "app/main.py" ]
