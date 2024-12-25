# Use nerfstudio as base image
FROM ghcr.io/nerfstudio-project/nerfstudio:latest

# Set working directory
WORKDIR /app

# Copy your Flask application
COPY . /app/

# Install additional Python packages
RUN pip install flask gunicorn

# Create necessary directories
RUN mkdir -p video sparse_reconstruction dense_reconstruction

# Make port 5000 available
EXPOSE 5000

# Create start script
RUN echo '#!/bin/bash\n\
gunicorn --bind 0.0.0.0:5000 wsgi:app' > /app/start.sh && \
    chmod +x /app/start.sh

# Command to run the application
CMD ["/app/start.sh"]