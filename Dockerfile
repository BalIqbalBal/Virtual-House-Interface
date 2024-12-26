FROM ghcr.io/nerfstudio-project/nerfstudio:latest

# Set working directory (creates /app if it doesn't exist)
WORKDIR /app

# Install curl and pip in a single layer
RUN apt-get update && apt-get install -y --no-install-recommends curl && \
    curl -sS https://bootstrap.pypa.io/get-pip.py | python && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install Flask
RUN pip install --no-cache-dir --upgrade pip flask

# Copy application code into the container
COPY . /app/

# Create other necessary directories
RUN mkdir -p /app/video /app/sparse_reconstruction /app/dense_reconstruction

# Expose port 5000 to the outside world
EXPOSE 5000

# Set the entrypoint to directly run the application
CMD ["python", "app.py"]
