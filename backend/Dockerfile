# Backend Dockerfile - FastAPI
FROM python:3.11-slim

WORKDIR /app

# Copy requirements first to leverage Docker layer cache
COPY requirements.txt .

# Install Python dependencies (no C compilation needed)
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# Copy the rest of the backend code
COPY . .

# Expose the API port
EXPOSE 8000

# Start the application using Gunicorn/Uvicorn
CMD ["gunicorn", "main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000"]
