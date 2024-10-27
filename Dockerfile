# Use an official Python image as the base
FROM python:3.9-slim

# Install dependencies
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean

# Copy the requirements and install
COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

# Copy application code
COPY app.py /app/app.py
WORKDIR /app

# Expose port 8080
EXPOSE 8080

# Run the Flask app
CMD ["python", "app.py"]
