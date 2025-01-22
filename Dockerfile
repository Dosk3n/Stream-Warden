# Base image with Python
FROM python:3.10-slim

# Set a descriptive working directory
WORKDIR /stream-warden

# Copy necessary files into the working directory
COPY stream_warden.py .
COPY config/ ./config/
COPY requirements.txt .
COPY logs/ ./logs/
# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the script
CMD ["python", "stream_warden.py"]
