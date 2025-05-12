# Use a minimal Python base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy your app files into the container
COPY . .

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose the port Koyeb will use
EXPOSE 5000

# Command to run your app
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
