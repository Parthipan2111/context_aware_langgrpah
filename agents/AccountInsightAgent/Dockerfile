# Use lightweight Python base
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Copy files
COPY account_insight_api.py /app/
COPY account_tools.py /app/
COPY prompt.py /app/
COPY __init__.py /app/
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose FastAPI port
EXPOSE 8001

# Run FastAPI with uvicorn
CMD ["uvicorn", "account_insight_api:app", "--host", "0.0.0.0", "--port", "8001"]
