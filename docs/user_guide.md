# User Guide for HED Web Tools

## Running locally

This project contains the web interface code for deploying HED tools as a web application running in a docker module.   

### Clone the repository
To run the web application locally, you will need to clone the `hed-web` repository.
```
git clone https://github.com/hed-standard/hed-web
```

### Setup configuration
You must have a `config.py` file in the root directory of your repository:

   1.  Copy `config_template.py` to `config.py`
   2.  Change `BASE_DIRECTORY` in the `Config` class in `config.py` to point to the directory that
       you want the application to use to temporarily store uploads and to cache the
       HED schema.

### Virtual environments

It is recommended to use a virtual environment to avoid conflicts with other Python packages.

1. Create a virtual environment:
   ```
   python -m venv .venv
   ```

2. Activate the virtual environment:
   - On Windows:
     ```
     .venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```
     source .venv/bin/activate
     ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

### Using conda (alternative)
1. Create a conda environment:
   ```
   conda create -n .venv python=3.10
   ```

2. Activate the environment:
   ```
   conda activate .venv
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

### Running the application
Once this installation is complete, you can execute `runserver`.
This call should bring up a Flask test server.
Paste the indicated link into a web browser, and you are ready to go.

## Deployment on an external webserver

### Overview
The `deploy_hed` directory contains scripts and configuration files that are needed
to deploy the application as a docker container.
These instructions assume that you have a Linux server with apache2 and docker installed.  

The current setup assumes that an apache web server runs inside a docker container
using internal port 80.
The docker container listens to requests on port 33000 from the local host IP
(assumed to be 127.0.0.1) of the Linux server running the docker container.
Docker forwards these requests and subsequent responses to and from its
internal server running on port 80.

If you are on the Linux server, you can run the online tools directly in a web 
browser using the address http://127.0.0.1:33000/hed.
In a production environment, the tools are meant to be run through an Apache web server with proxies.
The description of how to set this up is described elsewhere.

### Deploying the docker module

The instructions assume that you are in your home directory on the Linux server.
The deployment will use your home directory as a temporary staging area.
The instructions assume that you have DOCKER installed.

1. Make a deployment directory, say `deploy_hed`.
2. Download the
[hed-web deployment script](https://raw.githubusercontent.com/hed-standard/hed-web/master/deploy_hed/deploy.sh)
to your `deploy_hed` directory.
3. Change to the `deploy_hed` directory:

```  
   cd ~/deploy_hed
```
4. Execute the `deploy.sh` script:

```  
   sudo bash deploy.sh [branch] [environment]
```

**Command line options:**
- `branch` (optional): Specifies which git branch to deploy from. Defaults to `main` if not specified.
- `environment` (optional): Deployment environment, either `prod` or `dev`. Defaults to `prod` if not specified.

The `prod` environment deploys to `/hed` and uses the `hedtools` container,
while the `dev` environment deploys to `/hed_dev` and uses the `hedtools_dev` container.

**Examples:**
- Deploy production environment from main branch (default):
  ```
  sudo bash deploy.sh
  ```
- Deploy development environment:
  ```
  sudo bash deploy.sh main dev
  ```
- Deploy from a specific branch:
  ```
  sudo bash deploy.sh develop prod
  ```
- Deploy development environment from develop branch:
  ```
  sudo bash deploy.sh develop dev
  ```

**Environment differences:**

| Item               | Production | Development |
|--------------------|------------|-------------|
| Port               | 33000 | 33004 |
| URL Prefix         | `/hed` | `/hed_dev` |
| HED package source | PyPI hedtools package | Main branch hedtools package |
| Container name     | `hedtools` | `hedtools_dev` |

## Branches and versions

The web tools are built on the `hedtools` package housed in the `hed-python`
GitHub repository.
The tools are related to the `hed-specification` and `hed-schemas` repositories.
The branches correspond as follows:

| Branch |  Meaning | Synchronized with |
| ------ | -------- | ------------------ |
| stable | Tagged as a released version - will not change. | `stable@hed-python`<br/>`stable@hed-specification`<br/>`stable@hed-examples` |
| master | Most recent usable version.<br/>[https://hedtools/edu/hed](https://hedtools/edu/hed). | `master@hed-python`<br/>`master@hed-specification`<br/>`main@hed-examples` |
| develop | Experimental and evolving.<br/>[https://hedtools/edu/hed_dev](https://hedtools/edu/hed_dev). | `develop@hed-python`<br/>`develop@hed-specification`<br/>`develop@hed-examples` |


More information about using the webtools can be found at [https://www.hed-resources.org](https://www.hed-resources.org).

## Building the docs locally

To build and view the documentation locally:

```code

# Install mkdocs and the required plugins:
pip install -r docs/requirements.txt


mkdocs build

# For live development with auto-reload:
mkdocs serve
```
The documentation will be available at http://localhost:8000 when using mkdocs serve.