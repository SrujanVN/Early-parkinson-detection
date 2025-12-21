FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for audio and image processing
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    pkg-config \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn
RUN pip install --no-cache-dir scikit-image

# Copy application code and models
COPY . .

# Ensure upload directories exist
RUN mkdir -p uploads/audio uploads/mri uploads/handwriting

# Expose port
EXPOSE 5000

# Run with Gunicorn for production
# Increased timeout due to large model loading
# CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "4", "--timeout", "300", "app:app"]
CMD ["python", "app.py"]
