FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
COPY post_deals.py .
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python3", "post_deals.py"]
