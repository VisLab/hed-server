# HED Web Tools — User Guide

## Overview

HED Web Tools is a web-based application for working with HED (Hierarchical Event Descriptors) data. This guide will help you get the application running locally for development, deployed on a server for production, or integrated into your existing infrastructure.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Local Development Setup](#local-development-setup)
3. [Documentation Development](#documentation-development)
4. [Production Deployment](#production-deployment)
5. [Reverse Proxy Setup](#reverse-proxy-setup)
6. [Configuration Reference](#configuration-reference)
7. [Troubleshooting](#troubleshooting)
8. [Getting Help](#getting-help)

---

## Quick Start

Choose the option that best fits your needs:

### 🚀 Local Development (Windows/macOS/Linux)

Perfect for trying out the application or contributing to development:

```bash
git clone https://github.com/hed-standard/hed-web
cd hed-web
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
cp config_template.py config.py  # Windows: copy config_template.py config.py
hedweb --host 127.0.0.1 --port 5000 --debug
```

Then open: http://127.0.0.1:5000

### 🐳 Production Deployment (Ubuntu Server with Docker)

Ideal for production servers with Docker support:

```bash
mkdir -p ~/deploy_hed && cd ~/deploy_hed
curl -fsSL -o deploy.sh https://raw.githubusercontent.com/hed-standard/hed-web/main/deploy/deploy.sh
chmod +x deploy.sh
sudo ./deploy.sh main prod 127.0.0.1
```

Then configure your reverse proxy to point to localhost:33000

### 📚 Documentation Development

For working on documentation:

```bash
pip install -r docs/requirements.txt
mkdocs serve
# Open http://localhost:8000
```

---

## Local Development Setup

### Prerequisites

Before you begin, ensure you have:

- **Python 3.10 or higher** - [Download Python](https://www.python.org/downloads/)
- **Git** - [Download Git](https://git-scm.com/downloads)
- **Basic command line knowledge**

### Step-by-Step Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/hed-standard/hed-web
cd hed-web
```

#### 2. Set Up Virtual Environment

We recommend using a virtual environment to isolate dependencies:

**Option A: Using venv (recommended)**
```bash
python -m venv .venv

# Activate the environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
```

**Option B: Using conda**
```bash
conda create -n hedweb python=3.10
conda activate hedweb
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt

# Optional: Install in development mode to enable console commands
pip install -e .
```

#### 4. Configure the Application

Create your configuration file:

```bash
# Windows:
copy config_template.py config.py
# macOS/Linux:
cp config_template.py config.py
```

**Important**: Edit `config.py` and set `Config.BASE_DIRECTORY` to a directory you own. This directory will contain:
- `<BASE_DIRECTORY>/log` - Application logs
- `<BASE_DIRECTORY>/schema_cache` - HED schema cache files

Example configuration:
```python
# In config.py
class Config:
    BASE_DIRECTORY = r'C:\HEDWeb\data'  # Windows
    # BASE_DIRECTORY = '/home/user/hedweb_data'  # Linux/macOS
```

#### 5. Start the Development Server

**Option A: Using console script (after `pip install -e .`)**
```bash
hedweb --host 127.0.0.1 --port 5000 --debug
```

**Option B: Using Python module**
```bash
python -m hedweb.runserver --host 127.0.0.1 --port 5000 --debug
```

#### 6. Access the Application

Open your web browser and navigate to: **http://127.0.0.1:5000**

### Development Notes

- **Configuration Priority**: The app checks for `HEDTOOLS_CONFIG_CLASS` environment variable first, then tries `config.DevelopmentConfig`, and falls back to `default_config.DevelopmentConfig`
- **Static Files**: `STATIC_URL_PATH` and `URL_PREFIX` are not needed for local development
- **Hot Reload**: Use the `--debug` flag for automatic reloading during development

---

## Documentation Development

If you want to work on the documentation or build it locally:

### Setup

```bash
# Install documentation dependencies
pip install -r docs/requirements.txt
```

### Build Documentation

```bash
# Build static documentation
mkdocs build

# Serve with live reload (recommended for development)
mkdocs serve
```

The documentation will be available at: **http://localhost:8000**

### Documentation Structure

- `docs/` - Main documentation directory
- `mkdocs.yml` - MkDocs configuration
- `docs/requirements.txt` - Documentation-specific dependencies

---

## Production Deployment

### Docker Deployment on Ubuntu

This section covers deploying HED Web Tools using Docker on an Ubuntu server. This approach is recommended for production environments.

#### Prerequisites

- Ubuntu server with sudo access
- Docker Engine installed
- Internet connectivity

#### Install Docker

If Docker is not already installed:

```bash
sudo apt update
sudo apt install -y docker.io docker-compose-plugin
sudo systemctl enable --now docker
sudo usermod -aG docker "$USER"
# Log out and back in for group changes to take effect
```

#### Automated Deployment

We provide a deployment script that handles the entire process:

```bash
# Create deployment directory
mkdir -p ~/deploy_hed && cd ~/deploy_hed

# Download deployment script (main branch)
curl -fsSL -o deploy.sh \
  https://raw.githubusercontent.com/hed-standard/hed-web/main/deploy/deploy.sh
chmod +x deploy.sh
```

#### Deployment Options

The deployment script accepts three parameters:

```bash
./deploy.sh [branch] [environment] [bind_address]
```

- **branch**: Git branch to deploy (default: `main`)
- **environment**: `prod` or `dev` (default: `prod`)
- **bind_address**: IP to bind host port (default: `0.0.0.0`)

#### Common Deployment Scenarios

**Production deployment (public access):**
```bash
sudo ./deploy.sh main prod
# Accessible at: http://SERVER_IP:33000/hed
```

**Production deployment (localhost only, for reverse proxy):**
```bash
sudo ./deploy.sh main prod 127.0.0.1
# Accessible at: http://localhost:33000/hed
```

**Development deployment:**
```bash
sudo ./deploy.sh main dev
# Accessible at: http://SERVER_IP:33004/hed_dev
```

**Deploy from development branch:**
```bash
sudo ./deploy.sh develop prod
```

#### What the Deployment Script Does

1. Clones the HED Web repository at the specified branch
2. Copies deployment configuration files
3. Builds a Docker image with the appropriate configuration:
   - **Production**: `hedtools:latest`, URL prefix `/hed`, port 33000
   - **Development**: `hedtools_dev:latest`, URL prefix `/hed_dev`, port 33004
4. Runs the container with Gunicorn as the WSGI server
5. Configures environment variables for URL prefixes and static paths

#### Verify Deployment

Check that the container is running:

```bash
sudo docker ps
```

You should see output similar to:
```
CONTAINER ID   IMAGE            PORTS                     NAMES
abcdef123456   hedtools:latest  127.0.0.1:33000->80/tcp  hedtools
```

Test in your browser:
- **Production**: http://SERVER_IP:33000/hed
- **Development**: http://SERVER_IP:33004/hed_dev

#### Security Considerations

- **Firewall**: For security, bind to `127.0.0.1` and use a reverse proxy
- **Access Control**: Use UFW or security groups to limit access
- **HTTPS**: Always use HTTPS in production (see reverse proxy section)

---

## Reverse Proxy Setup

For production deployments, it's recommended to use a reverse proxy (Apache or Nginx) in front of the Docker container. This provides better security, SSL termination, and additional features.

### Apache Reverse Proxy

#### Install and Configure Apache

```bash
sudo apt update
sudo apt install -y apache2
sudo a2enmod proxy proxy_http headers
```

#### Optional: Set Global ServerName

To silence Apache warnings:

```bash
echo "ServerName $(hostname -f || hostname)" | sudo tee /etc/apache2/conf-available/servername.conf
sudo a2enconf servername
```

#### Create Site Configuration

```bash
sudo tee /etc/apache2/sites-available/hed.conf << 'EOF'
<VirtualHost *:80>
    ServerName example.com
    ServerAdmin admin@example.com

    # Proxy HED application
    ProxyPreserveHost On
    RequestHeader set X-Forwarded-Proto expr=%{REQUEST_SCHEME}
    ProxyPass        /hed     http://127.0.0.1:33000/hed
    ProxyPassReverse /hed     http://127.0.0.1:33000/hed

    # Security and performance settings
    <Location /hed>
        Require all granted
        ProxyPassReverseCookiePath / /hed
    </Location>

    # Logging
    ErrorLog ${APACHE_LOG_DIR}/hed-error.log
    CustomLog ${APACHE_LOG_DIR}/hed-access.log combined
</VirtualHost>
EOF

# Enable the site
sudo a2ensite hed.conf
sudo systemctl reload apache2
```

#### Configure Firewall

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Apache Full'
sudo ufw enable
sudo ufw status
```

#### Enable HTTPS with Let's Encrypt

```bash
sudo apt install -y certbot python3-certbot-apache
sudo certbot --apache -d example.com

# Test automatic renewal
sudo systemctl list-timers | grep certbot
sudo certbot renew --dry-run
```

### Nginx Reverse Proxy (Alternative)

#### Install Nginx

```bash
sudo apt update
sudo apt install -y nginx
```

#### Create Site Configuration

```bash
sudo tee /etc/nginx/sites-available/hed << 'EOF'
server {
    listen 80;
    server_name example.com;

    location /hed/ {
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_pass http://127.0.0.1:33000/hed/;
        
        # Optional: increase timeouts for large uploads
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
    }
}
EOF

# Enable the site
sudo ln -s /etc/nginx/sites-available/hed /etc/nginx/sites-enabled/hed
sudo nginx -t
sudo systemctl reload nginx
```

#### Enable HTTPS with Let's Encrypt

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d example.com
```

---

## Configuration Reference

### Local Development Configuration

When running locally, configuration is managed through `config.py` (copied from `config_template.py`):

```python
class Config:
    # Base directory for application data
    BASE_DIRECTORY = '/path/to/your/data/directory'
    
    # Derived paths (automatically set)
    LOG_DIRECTORY = os.path.join(BASE_DIRECTORY, 'log')
    LOG_FILE = 'hed_web.log'
    HED_CACHE_FOLDER = os.path.join(BASE_DIRECTORY, 'schema_cache')
    
    # URL configuration (usually None for local)
    URL_PREFIX = None
    STATIC_URL_PATH = None
```

### Docker Production Configuration

The Docker deployment uses environment variables for configuration:

- `HED_URL_PREFIX` (default: `/hed` for prod, `/hed_dev` for dev)
- `HED_STATIC_URL_PATH` (default: `/hed/hedweb/static`)

These are automatically set by the deployment script.

### Environment Variables

The application respects these environment variables:

- `HEDTOOLS_CONFIG_CLASS` - Override configuration class
- `HED_URL_PREFIX` - URL prefix for the application
- `HED_STATIC_URL_PATH` - Static files URL path

---

## Troubleshooting

### Common Issues and Solutions

#### Local Development Issues

**Problem**: `hedweb` command not found
```bash
# Solution: Install in development mode
pip install -e .
```

**Problem**: Permission errors with BASE_DIRECTORY
```bash
# Solution: Ensure the directory exists and is writable
mkdir -p /path/to/your/data/directory
chmod 755 /path/to/your/data/directory
```

**Problem**: Port already in use
```bash
# Solution: Use a different port
hedweb --host 127.0.0.1 --port 5001 --debug
```

#### Docker Deployment Issues

**Problem**: Check if container is running
```bash
sudo docker ps
sudo docker ps -a  # Show stopped containers
```

**Problem**: View container logs
```bash
sudo docker logs hedtools
sudo docker logs -f hedtools  # Follow logs in real-time
```

**Problem**: Container won't start
```bash
# Check Docker daemon
sudo systemctl status docker

# Restart Docker service
sudo systemctl restart docker
```

**Problem**: Remove and rebuild container
```bash
# Stop and remove container
sudo docker stop hedtools
sudo docker rm hedtools

# Remove old image
sudo docker rmi hedtools:latest

# Re-run deployment script
sudo ./deploy.sh main prod 127.0.0.1
```

#### Docker Management Commands

```bash
# List all containers
sudo docker ps -a

# List all images
sudo docker images

# Remove unused images
sudo docker image prune

# Remove dangling images
sudo docker rmi $(sudo docker images -f "dangling=true" -q)

# Access container shell for debugging
sudo docker exec -it hedtools /bin/bash

# View container resource usage
sudo docker stats hedtools
```

#### Reverse Proxy Issues

**Problem**: 502 Bad Gateway
- Check if the Docker container is running
- Verify the proxy configuration points to the correct port
- Check firewall settings

**Problem**: Static files not loading
- Ensure `STATIC_URL_PATH` is correctly configured
- Check proxy configuration for static file handling

#### Performance Issues

**Problem**: Slow response times
- Increase Gunicorn worker processes in Docker
- Add more memory to the server
- Use Nginx for static file serving

---

## Advanced Configuration

### Package Installation

To install HED Web Tools as a Python package:

```bash
pip install -e .
```

This enables the `hedweb` console command and makes the package importable.

### Custom Configuration Classes

You can create custom configuration classes by inheriting from the base configuration:

```python
# In config.py
class CustomConfig(Config):
    DEBUG = False
    LOG_LEVEL = 'INFO'
    # Add your custom settings here
```

Then set the environment variable:
```bash
export HEDTOOLS_CONFIG_CLASS=config.CustomConfig
```

---

## Getting Help

### Resources

- **GitHub Issues**: [Report bugs and request features](https://github.com/hed-standard/hed-web/issues)
- **HED Resources**: [Official HED documentation](https://www.hed-resources.org)
- **HED Specification**: [HED standard specification](https://hed-specification.readthedocs.io/)

### Support

When reporting issues, please include:

1. Your operating system and version
2. Python version (`python --version`)
3. Installation method (local, Docker, etc.)
4. Error messages or logs
5. Steps to reproduce the issue

### Contributing

We welcome contributions! Please see the project repository for contribution guidelines.

---

*Last updated: August 2025*
