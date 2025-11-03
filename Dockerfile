FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY log_generator.py .
COPY config.yaml .

# Expose health check port
EXPOSE 8080

# Run the log generator
CMD ["python", "-u", "log_generator.py"]
