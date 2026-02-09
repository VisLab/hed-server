FROM python:3.10-slim-bullseye

# Set the working directory inside the container
WORKDIR /root

# Copy project metadata files needed for pip install
COPY pyproject.toml README.md ./
COPY setup.py* ./

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    git \
    musl-dev \
    logrotate \
    libxslt-dev \
    libxml2-dev && \
    pip3 install --upgrade pip

# Copy the hedweb package to match pyproject.toml structure
COPY ./hedtools/hedweb ./hedweb/

# Install the package with production dependencies (gunicorn)
RUN pip3 install .[prod]

# Install HEDTools based on the environment
ARG HED_INSTALL_SOURCE=pypi
ARG CACHE_BUST
RUN if [ "$HED_INSTALL_SOURCE" = "main" ]; then \
        echo "Installing hedtools from GitHub main branch..."; \
        pip3 install --no-cache-dir git+https://github.com/hed-standard/hed-python.git@main || exit 1; \
    else \
        echo "Installing hedtools from PyPI..."; \
        pip3 install --no-cache-dir hedtools || exit 1; \
    fi

# Create necessary directories and set permissions
RUN mkdir -p /var/log/hedtools && \
    chown -R www-data:www-data /var/log/hedtools && \
    mkdir -p /var/cache/schema_cache && \
    chown -R www-data:www-data /var/cache/schema_cache

# Ensure Python can import the application package
ENV PYTHONPATH="/root"

# Set environment variables for the application
ENV HEDTOOLS_CONFIG_CLASS=config.ProductionConfig

# Copy the logrotate configuration for Gunicorn
COPY gunicorn-logrotate.conf /etc/logrotate.d/gunicorn

# Expose the Gunicorn port (80 by default)
EXPOSE 80

# Run the Flask application with Gunicorn, binding to port 80
# Import path matches PYTHONPATH layout (/root contains the 'hedweb' package)
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:80", "--forwarded-allow-ips=127.0.0.1", \
     "--access-logfile", "/var/log/hedtools/access.log", \
     "--error-logfile", "/var/log/hedtools/error.log",  "--capture-output",\
     "--log-level", "info", "hedweb.runserver:app"]
