# Use an official Python image as a base
FROM python:3.10-slim

# Set the working directory
WORKDIR /brokencloud


# Install required system packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Default port (can be overridden)
ENV PORT=50051
ENV HOST=0.0.0.0

EXPOSE 50051

# Start the gRPC server
CMD ["python", "brokencloud/nobel_prize_grpc_server.py"]
