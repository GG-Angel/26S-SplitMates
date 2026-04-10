FROM python:3.12-slim

WORKDIR /seeder

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY seed.py .

CMD ["python", "seed.py"]
