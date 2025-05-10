# =====================================
# 4. Dockerfile for order_lookup_service
# =====================================
# File: order_lookup_service/Dockerfile
FROM python:3.10
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]