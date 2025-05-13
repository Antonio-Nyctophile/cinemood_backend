# Use a minimal Python base image
FROM python:3.9-slim

# Disable stdout buffering for real-time logs
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy only necessary files
COPY . .

# Install dependencies with retry support
RUN pip install --upgrade pip && \
    pip install --retries 5 --timeout 60 -r requirements.txt

# Expose the port used by the app
EXPOSE 5000

# Start the app using gunicorn
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
