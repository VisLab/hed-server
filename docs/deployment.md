# HEDTools online deployment

This guide provides step-by-step instructions for deploying and using HED online tools in various environments, from local development to production Docker deployments.

## Installation

### Prerequisites

- **Python 3.10 or higher** — [Download Python](https://www.python.org/downloads/)
- **Git** — [Download Git](https://git-scm.com/downloads/)

For Docker deployment:

- **Docker** — [Get Docker](https://docs.docker.com/get-docker/)
- **Ubuntu Server** (recommended for production)

### Clone the repository

```bash
git clone https://github.com/hed-standard/hed-server
cd hed-server
```

## Local development setup

### 1. Create and activate virtual environment

**Windows (PowerShell):**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS/Linux:**

```bash
python -m venv .venv
source .venv/bin/activate
```

```{note}
You'll need to activate the virtual environment every time you work on the project in a new terminal session.
```

### 2. Install dependencies

Install the package with development dependencies:

```bash
pip install -e .[dev]
```

For documentation building:

```bash
pip install -e .[docs]
```

### 3. Create configuration file

Copy the configuration template:

**Windows:**

```powershell
Copy-Item config_template.py config.py
```

**macOS/Linux:**

```bash
cp config_template.py config.py
```

### 4. Run the development server

```bash
python hedweb/runserver.py
```

Or use the command-line interface:

```bash
python -m hedweb.runserver --host 127.0.0.1 --port 5000 --debug
```

### 5. Access the application

Open your browser and navigate to: **http://127.0.0.1:5000**

```{note}
The development server includes debug mode with auto-reload on code changes.
```

## Docker deployment

### Quick deployment

The simplest way to deploy using Docker is with the provided deployment script:

```bash
# Create deployment directory
mkdir -p ~/deploy_hed
cd ~/deploy_hed

# Download deployment script
curl -fsSL -o deploy.sh https://raw.githubusercontent.com/hed-standard/hed-server/main/deploy/deploy.sh

# Make script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh main prod
```

### Deployment script options

The `deploy.sh` script accepts three optional parameters:

```bash
./deploy.sh [branch] [environment] [bind_address]
```

- **branch**: Git branch to deploy (default: `main`)
- **environment**: `prod` or `dev` (default: `prod`)
- **bind_address**: IP address to bind (default: `0.0.0.0`, use `127.0.0.1` for localhost-only)

**Examples:**

```bash
# Production deployment from main branch
./deploy.sh main prod

# Development deployment from develop branch
./deploy.sh develop dev

# Localhost-only deployment
./deploy.sh main prod 127.0.0.1
```

### Environment-specific configurations

**Production environment (`prod`):**

- Container name: `hedtools`
- Host port: `33000`
- URL prefix: `/hed`
- HED source: PyPI release (`hedtools` package)

**Development environment (`dev`):**

- Container name: `hedtools_dev`
- Host port: `33004`
- URL prefix: `/hed_dev`
- HED source: GitHub main branch

### Manual Docker build

If you prefer manual control over the Docker build:

```bash
# Build the Docker image
docker build -t hedtools:latest \
  --build-arg HED_INSTALL_SOURCE=pypi \
  --build-arg CACHE_BUST=$(date +%s) \
  -f deploy/Dockerfile .

# Run the container
docker run -d \
  --name hedtools \
  -p 33000:80 \
  -e HED_URL_PREFIX=/hed \
  -e HED_STATIC_URL_PATH=/hed/hedweb/static \
  hedtools:latest
```

### Docker management commands

```bash
# Check container status
docker ps

# View container logs
docker logs hedtools

# Stop the container
docker stop hedtools

# Remove the container
docker rm hedtools

# Restart the container
docker restart hedtools
```

## Production deployment

### Reverse proxy setup with Nginx

For production deployments, use Nginx as a reverse proxy in front of the Docker container.

#### 1. Install Nginx

```bash
sudo apt update
sudo apt install nginx
```

#### 2. Configure Nginx

Create a new Nginx configuration file at `/etc/nginx/sites-available/hedtools`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /hed {
        proxy_pass http://localhost:33000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Handle large file uploads
        client_max_body_size 100M;
        proxy_read_timeout 300s;
        proxy_connect_timeout 300s;
    }

    location /hed/hedweb/static {
        proxy_pass http://localhost:33000;
        proxy_set_header Host $host;
        
        # Cache static files
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

#### 3. Enable the site

```bash
sudo ln -s /etc/nginx/sites-available/hedtools /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### SSL/TLS setup with Let's Encrypt

Secure your deployment with HTTPS using Certbot:

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com

# Verify auto-renewal
sudo certbot renew --dry-run
```

### Deployment with both prod and dev versions

To run both production and development versions simultaneously:

```bash
# Deploy production version
./deploy.sh main prod

# Deploy development version
./deploy.sh develop dev
```

Update your Nginx configuration to handle both:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Production version
    location /hed {
        proxy_pass http://localhost:33000;
        # ... other proxy settings
    }

    # Development version
    location /hed_dev {
        proxy_pass http://localhost:33004;
        # ... other proxy settings
    }
}
```

## Configuration

### Configuration file structure

The application uses a Python-based configuration system. Edit `config.py` to customize settings:

```python
import os

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = '/tmp/hed_uploads'
    
    # HED schema settings
    HED_CACHE_FOLDER = '/var/cache/schema_cache'
    
    # Flask settings
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
```

### Environment variables

The application recognizes these environment variables:

| Variable                | Description                                                                                                                               | Default                   |
| ----------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- | ------------------------- |
| `HEDTOOLS_CONFIG_CLASS` | Configuration class to use                                                                                                                | `config.ProductionConfig` |
| `HED_URL_PREFIX`        | URL prefix for the application                                                                                                            | `/hed`                    |
| `HED_STATIC_URL_PATH`   | Path to static files                                                                                                                      | `/hed/hedweb/static`      |
| `SECRET_KEY`            | Flask secret key for sessions                                                                                                             | Generated                 |
| `HED_GITHUB_TOKEN`      | GitHub token used by hedtools when fetching HED schema versions from the GitHub API (raises the rate limit from 60 to 5000 requests/hour) | Unset (unauthenticated)   |

### Docker environment variables

When running in Docker, set environment variables in the `docker run` command:

```bash
docker run -d \
  --name hedtools \
  -p 33000:80 \
  -e HED_URL_PREFIX=/hed \
  -e SECRET_KEY=your-production-secret-key \
  hedtools:latest
```

## Using the web interface

### Available tools

The HED online interface provides several categories of operations:

**Events operations (for tabular files):**

- Validate HED annotations in tabular files
- Assemble HED strings from tabular data
- Search HED annotations with query syntax
- Generate sidecar templates from tabular files
- Execute remodeling scripts

**Sidecar operations:**

- Validate BIDS JSON sidecars
- Convert HED tags to long/short form
- Extract spreadsheet templates from sidecars
- Merge spreadsheet data into sidecars

**Spreadsheet operations:**

- Validate HED in spreadsheet files
- Convert spreadsheets to long/short form

**String operations:**

- Validate individual HED strings
- Convert strings to long/short form
- Search

**Schema operations:**

- Validate HED schema files
- Convert schema formats
- Check for schema issues

### File upload guidelines

- **Maximum file size**: 16MB (configurable)
- **Supported formats**: TSV, Excel (.xlsx, .xls), JSON
- **Encoding**: UTF-8 recommended

### Workflow example

1. Navigate to **Events** > **Validate events file**
2. Upload your tabular file (`.tsv`)
3. Optionally upload a JSON sidecar
4. Select HED schema version
5. Click **Validate**
6. Review validation results
7. Download validation report if needed

## REST API access

### API overview

All HED operations available through the web interface can also be accessed programmatically via REST API endpoints. The API accepts multipart/form-data requests and returns JSON responses.

### API endpoint structure

```
POST /services/<operation_category>/<operation_name>
```

Examples:

- `/services/events/validate`
- `/services/sidecars/validate`
- `/services/strings/validate`

### Example: Validating a HED string

**Python example:**

```python
import requests

url = "http://localhost:5000/services/strings/validate"

# Prepare request
files = {
    'schema_version': (None, '8.2.0'),
    'hed_strings': (None, 'Sensory-event, Visual-presentation'),
    'check_for_warnings': (None, 'on')
}

# Send request
response = requests.post(url, files=files)
result = response.json()

if result.get('error_type'):
    print(f"Error: {result['error_type']}")
    print(result.get('error_msg'))
else:
    print("Validation successful!")
    if result.get('data'):
        print(f"Issues found: {result['data']}")
```

### Example: Validating an events file

**Python example:**

```python
import requests

url = "http://localhost:5000/services/events/validate"

# Prepare files
with open('events.tsv', 'rb') as events_file:
    files = {
        'events_file': ('events.tsv', events_file, 'text/tab-separated-values'),
        'schema_version': (None, '8.2.0'),
        'check_for_warnings': (None, 'on')
    }
    
    response = requests.post(url, files=files)
    result = response.json()
    
    if result.get('error_type'):
        print(f"Error: {result['error_type']}")
    else:
        print("Validation complete")
        print(result.get('msg_category'))
```

### API response format

All API responses follow this JSON structure:

```json
{
    "error_type": "",
    "error_msg": "",
    "service": "operation_name",
    "results": {},
    "msg_category": "success|warning|error",
    "msg": "Human-readable message"
}
```

### Complete API documentation

For complete API documentation including all available endpoints, parameters, and response formats, see the [API Reference](api/index.rst).

## Troubleshooting

### Common issues

#### Application won't start

**Symptoms:** Import errors or module not found

**Solutions:**

1. Verify Python version: `python --version` (must be 3.10+)
2. Ensure virtual environment is activated
3. Reinstall dependencies: `pip install -e .[dev]`
4. Check for conflicting packages: `pip list`

#### Port already in use

**Symptoms:** `Address already in use` error

**Solutions:**

**Windows (PowerShell):**

```powershell
# Find process using port 5000
netstat -ano | findstr :5000

# Kill process (replace PID)
taskkill /PID <PID> /F
```

**Linux/macOS:**

```bash
# Find and kill process
lsof -ti:5000 | xargs kill -9
```

#### Docker container exits immediately

**Symptoms:** Container starts but immediately stops

**Solutions:**

1. Check container logs:
   ```bash
   docker logs hedtools
   ```
2. Inspect container:
   ```bash
   docker inspect hedtools
   ```
3. Verify configuration files are present
4. Check file permissions in the container

#### Schema validation errors

**Symptoms:** "Could not load HED schema" errors

**Solutions:**

1. Check internet connectivity (some schemas are fetched from GitHub)
2. Verify schema version exists
3. Use a local schema file if network is unavailable
4. Check cache directory permissions

#### Schema version dropdown doesn't populate (works locally, fails on some remote hosts)

**Symptoms:** The schema-version dropdown works when the server runs on a local network but comes up empty (or only shows one or two versions, such as a single prerelease) when the same image is deployed on a remote/cloud host.

**Cause:** hedtools populates this list by calling the GitHub REST API (`api.github.com/repos/hed-standard/hed-schemas/...`). Unauthenticated calls to that API are capped at 60 requests/hour **per source IP**. A shared cloud or data-center IP is much more likely to already be near that limit than a home/office IP, and once it's hit, hedtools' schema cache silently falls back to whatever's already cached (including any schema versions bundled inside the installed `hedtools` package itself, which can explain a single version showing up even when nothing new could be fetched). This is a GitHub API rate limit, not a bug in hed-server's Docker image.

**Solutions:**

1. From inside the running container, check whether the GitHub API is even reachable and what quota remains. Run this **unauthenticated** check first:

   ```bash
   docker exec -it <container_name> curl -s https://api.github.com/rate_limit
   ```

   A `403`/near-zero `remaining` count (under a `"rate"` object showing `"limit": 60`) confirms the unauthenticated quota is exhausted; a connection error/timeout instead points to a network/firewall restriction on the host rather than a quota issue.

   This command alone can't tell you whether a token is actually helping, though - it never sends one, so it always reports the unauthenticated 60/hour pool regardless of what's configured. If `HED_GITHUB_TOKEN` is already set in the container, check that pool specifically:

   ```bash
   docker exec -it <container_name> sh -c 'curl -s -H "Authorization: token $HED_GITHUB_TOKEN" https://api.github.com/rate_limit'
   ```

   This should show `"limit": 5000`. If it does but the dropdown still doesn't populate, the token itself isn't the problem - look elsewhere (e.g. confirm `HED_GITHUB_TOKEN` is actually set inside the container with `docker exec <container_name> env | grep HED_GITHUB_TOKEN`, or revisit the network/firewall angle in step 3). If the authenticated check still shows `"limit": 60`, the token isn't being sent at all - the header may be malformed, the variable may be empty, or an invalid/expired token causes GitHub to silently fall back to unauthenticated treatment.

2. Supply a GitHub token (a plain personal access token, no special scopes needed - it's only used for read-only API calls). `deploy.sh` looks for one in this order and forwards whichever it finds into the container, raising the limit from 60 to 5000 requests/hour:

   1. `HED_GITHUB_TOKEN` or `GITHUB_TOKEN` in the environment of the shell that runs `deploy.sh`. **Note:** deployments here are typically run as `sudo bash deploy.sh ...`, and `sudo` resets the environment by default - `export HED_GITHUB_TOKEN=...` beforehand will *not* reach the script unless you specifically run `sudo -E bash deploy.sh ...` and your sudoers config permits `-E` to preserve that variable. Don't rely on this option unless you've confirmed it actually reaches the container (check the "Forwarding a GitHub token..." log line `deploy.sh` prints).
   2. A file at `deploy/.github_token`, inside whichever hed-server checkout is actually being deployed (gitignored - never commit it). This is the recommended option for `sudo bash deploy.sh` setups, since a plain file read is unaffected by sudo's environment reset:
      ```bash
      echo "ghp_yourtokenhere" | sudo tee /path/to/hed-server/deploy/.github_token
      sudo chmod 600 /path/to/hed-server/deploy/.github_token
      ```
      Create it once and every future deploy on that host picks it up automatically.
   3. A file at `/etc/hed-server/github_token`, for setups that re-clone the repo on every deploy (so a repo-relative file wouldn't persist) but still want one token shared across environments on that host.

3. If step 1 shows the API is unreachable rather than rate-limited, the fix is on the host/network side - outbound HTTPS to `api.github.com` and `raw.githubusercontent.com` needs to be allowed from wherever the container runs.

#### File upload fails

**Symptoms:** 413 Request Entity Too Large or upload timeout

**Solutions:**

1. Check file size (default limit: 16MB)
2. Increase `MAX_CONTENT_LENGTH` in config:
   ```python
   MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
   ```
3. For Nginx, update `client_max_body_size`
4. Check available disk space

### Performance issues

#### Slow validation

**Causes and solutions:**

- **Large files**: Process in batches or increase timeout
- **Complex schemas**: Use schema caching
- **Network issues**: Use local schema files

#### High memory usage

**Solutions:**

1. Limit concurrent requests
2. Increase Docker container memory:
   ```bash
   docker run -d --memory="2g" --name hedtools hedtools:latest
   ```

### Getting help

If you encounter issues not covered here:

1. **Check logs**:

   - Development: Console output
   - Docker: `docker logs hedtools`
   - Production: Check `/var/log/hedtools/`

2. **Search GitHub issues**: [hed-server issues](https://github.com/hed-standard/hed-server/issues)

3. **Create a new issue** with:

   - Detailed problem description
   - Steps to reproduce
   - Error messages and logs
   - Environment information (OS, Python version, deployment method)

## Best practices

### Security

- **Change default secret key** in production
- **Use HTTPS** (SSL/TLS) for production deployments
- **Keep software updated**: Regularly update dependencies
- **Limit file upload sizes** appropriately
- **Use environment variables** for sensitive configuration
- **Enable CSRF protection** (enabled by default)

### Performance

- **Use Docker** for consistent deployments
- **Enable caching** for HED schemas
- **Use a reverse proxy** (Nginx) in production
- **Monitor resource usage** and set appropriate limits
- **Use CDN** for static files if serving high traffic

### Maintenance

- **Regular backups** of configuration and logs
- **Monitor logs** for errors and warnings
- **Test updates** in development before production
- **Document custom configurations**
- **Keep deployment scripts** version-controlled

### Development

- **Use virtual environments** to isolate dependencies
- **Run tests** before committing changes
- **Format code** with `ruff format` before commits
- **Follow PEP 8** style guidelines
- **Write tests** for new features

## Additional resources

### Documentation

- **HED Standard**: [https://www.hedtags.org/](https://www.hedtags.org/)
- **HED Specification**: [https://hed-specification.readthedocs.io/](https://hed-specification.readthedocs.io/)
- **Python HEDTools**: [https://github.com/hed-standard/hed-python](https://github.com/hed-standard/hed-python)
- **HED schemas**: [https://github.com/hed-standard/hed-schemas](https://github.com/hed-standard/hed-schemas)

### Tools

- **HED online tools (production)**: [https://hedtools.org/hed](https://hedtools.org/hed)
- **HED online tools (Development)**: [https://hedtools.org/hed_dev](https://hedtools.org/hed_dev)
- **CTagger**: [https://github.com/hed-standard/CTagger](https://github.com/hed-standard/CTagger)

### Community

- **Issue tracker**: [hed-server issues](https://github.com/hed-standard/hed-server/issues)
- **HED maintainers email**: [hed.maintainers@gmail.com](mailto:hed.maintainers@gmail.com)

## Appendix: Quick reference

### Command reference

**Local development:**

```bash
# Activate virtual environment (Windows)
.venv\Scripts\Activate.ps1

# Activate virtual environment (Linux/macOS)
source .venv/bin/activate

# Install dependencies
pip install -e .[dev]

# Run development server
python hedweb/runserver.py
python -m hedweb.runserver --port 5000 --debug
```

**Docker deployment:**

```bash
# Quick deployment
./deploy.sh main prod

# Build image manually
docker build -t hedtools:latest -f deploy/Dockerfile .

# Run container
docker run -d --name hedtools -p 33000:80 hedtools:latest

# View logs
docker logs hedtools

# Stop/start/restart
docker stop hedtools
docker start hedtools
docker restart hedtools
```

**Testing:**

```bash
# Run all tests
python -m unittest discover

# Run specific test category
python -m unittest discover -s tests/
python -m unittest discover -s service_tests/

# Run with coverage
coverage run -m unittest discover
coverage report
```

**Documentation:**

```bash
# Build documentation
cd docs
python -m sphinx -b html . _build/html

# Serve with auto-reload (if sphinx-autobuild is installed)
python -m sphinx_autobuild . _build/html
```

### File locations

**Configuration:**

- Template: `config_template.py`
- Local: `config.py` (create from template)
- Docker: `/root/config.py` (copied from `deploy/base_config.py` during the image build)

**Logs (Docker):**

- Application: `/var/log/hedtools/`
- Gunicorn: `/var/log/hedtools/gunicorn.log`

**Cache:**

- Local: `/tmp/hed_cache` or configured location
- Docker: `/var/cache/schema_cache`

**Static files:**

- Source: `hedweb/static/`
- URL: `/hed/hedweb/static/` (in production)

### Port reference

| Deployment  | Container Port | Host Port | URL Prefix |
| ----------- | -------------- | --------- | ---------- |
| Production  | 80             | 33000     | /hed       |
| Development | 80             | 33004     | /hed_dev   |
| Local dev   | -              | 5000      | /          |

### Environment variables reference

| Variable                | Purpose                                                                | Default                   |
| ----------------------- | ---------------------------------------------------------------------- | ------------------------- |
| `HEDTOOLS_CONFIG_CLASS` | Config class                                                           | `config.ProductionConfig` |
| `HED_URL_PREFIX`        | URL prefix                                                             | `/hed`                    |
| `HED_STATIC_URL_PATH`   | Static files path                                                      | `/hed/hedweb/static`      |
| `SECRET_KEY`            | Flask secret key                                                       | Auto-generated            |
| `HED_INSTALL_SOURCE`    | Docker HED source                                                      | `pypi` or `main`          |
| `HED_GITHUB_TOKEN`      | GitHub token forwarded into the container for schema-version API calls | Unset                     |
