

FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies (for image processing and HEIC support)
RUN apt-get update && apt-get install -y \
    libheif1 libheif-dev libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source
COPY . .

# Expose the default port (update if your app uses a different one)
EXPOSE 8000

# Run the app
CMD ["python", "main.py"]