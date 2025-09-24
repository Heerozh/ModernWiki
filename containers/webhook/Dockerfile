FROM python:3.11-alpine

# Install Docker CLI and certificates
RUN apk add --no-cache docker-cli
# RUN apt-get update && apt-get install -y \
#     docker.io \
#     curl \
#     ca-certificates \
#     && rm -rf /var/lib/apt/lists/* \
#     && update-ca-certificates

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt

# Copy application
COPY app.py .

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]