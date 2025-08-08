FROM python:3.10-slim-bullseye

# Set the working directory inside the container
WORKDIR /root

# Copy the requirements file and install system dependencies
COPY . .
RUN apt-get update && apt-get install -y \
    gcc \
    git \
    musl-dev \
    logrotate \
    libxslt-dev \
    libxml2-dev && \
    pip3 install --upgrade pip && \
    pip3 install -r requirements.txt

# Install HEDTools based on the environment
ARG HED_INSTALL_SOURCE=pypi
ARG CACHE_BUST
RUN if [ "$HED_INSTALL_SOURCE" = "main" ]; then \
        pip3 install git+https://github.com/hed-standard/hed-python/@main; \
    else \
        pip3 install hedtools; \
    fi

# Create necessary directories and set permissions
RUN mkdir -p /var/log/hedtools && \
    chown -R www-data:www-data /var/log/hedtools && \
    mkdir -p /var/cache/schema_cache && \
    chown -R www-data:www-data /var/cache/schema_cache

# Copy the application code into the container
COPY ./hedtools /root/hedtools/
COPY ./hedtools/hedweb /root/hedtools/hedweb/

# Set the PYTHONPATH environment variable to include /root/hedtools
ENV PYTHONPATH="/root/hedtools"

# Set environment variables for the application
ENV HEDTOOLS_CONFIG_CLASS=config.ProductionConfig

# Copy the logrotate configuration for Gunicorn
COPY gunicorn-logrotate.conf /etc/logrotate.d/gunicorn

# Expose the Gunicorn port (80 by default)
EXPOSE 80

# Run the Flask application with Gunicorn, binding to port 80
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:80", "--forwarded-allow-ips=127.0.0.1", \
     "--access-logfile", "/var/log/hedtools/access.log", \
     "--error-logfile", "/var/log/hedtools/error.log",  "--capture-output",\
     "--log-level", "info", "hedtools.hedweb.runserver:app"]
