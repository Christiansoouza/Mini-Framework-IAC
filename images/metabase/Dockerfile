# Dockerfile exemplo para app1
FROM python:3.12-slim
WORKDIR /app
COPY src/ ./src/
RUN pip install --no-cache-dir -r src/requirements.txt
CMD ["python", "src/main.py"]
