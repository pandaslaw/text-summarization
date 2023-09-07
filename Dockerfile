# syntax=docker/dockerfile:1

# Install base Python image
FROM python:3.8-slim-buster

# Set working directory
WORKDIR /app

# Copy local files to the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Informs Docker that the container listens on port 4001
EXPOSE 8888


CMD ["python", "./main.py"]