# * Citation 6

# Base image
FROM python:3.10-slim-bullseye

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends --no-install-suggests \
    build-essential \
    libmariadb-dev gcc python3-dev musl-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Set working directory
WORKDIR /app

# Copy and install Python dependencies
COPY ./requirements.txt /app
RUN pip install --no-cache-dir --requirement /app/requirements.txt

# Copy application code
COPY . /app

# Expose port
EXPOSE 8080

# Command to run the application
CMD ["python3", "server.py"]
