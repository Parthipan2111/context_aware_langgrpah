# Use lightweight Python base
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Copy files
COPY auth.py /app/
COPY auth-service-api.py /app/
COPY __init__.py /app/
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose FastAPI port
EXPOSE 8004

# Run FastAPI with uvicorn
CMD ["uvicorn", "auth-service-api:app", "--host", "0.0.0.0", "--port", "8004"]
