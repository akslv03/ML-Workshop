FROM python:3.12-slim

WORKDIR /ml_worker

COPY requirements.txt /ml_worker/

RUN pip install --upgrade pip && pip install -r /ml_worker/requirements.txt

CMD ["python", "main.py"]
