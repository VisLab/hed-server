## hedweb
[![Documentation Status](https://readthedocs.org/projects/hed-web/badge/?version=latest)](https://hed-web.readthedocs.io/en/latest/?badge=latest)

### Online deployment
The stable version of the HED online tools is available for your use at:
[**https://hedtools.org/hed**](https://hedtools.org/hed).
An alternate version [**https://hedtools.org/hed_dev**](https://hedtools.org/hed_dev)
has the latest features, some of which are experimental.


### Running locally

This project contains the web interface code for deploying HED tools as a web application running in a docker module.   
The instructions assume that you have cloned the 
`hed-web` GitHub repository:

```
git clone https://github.com/hed-standard/hed-web
```

The application can be run locally on an internal test web server by calling 
the `runserver` application directly.
To do this you will have to do the following:

1. Set up a `config.py` in the same directory as `config_template.py`. 
   1.  Copy `config_template.py` to `config.py`
   2.  Change `BASE_DIRECTORY` in the `Config` class to point to the directory that
       you want the application to use to temporarily store uploads and to cache the
       HED schema.
2. Use `pip` to install `hedtools` from the 
[GitHub](https://github.com/hed-standard/hed-python) repository:

   ```
       pip install git+https://github.com/hed-standard/hed-python/@master
   ```

Once this installation is complete, you can execute `runserver`.
This call should bring up a Flask test server.
Paste the indicated link into a web browser, and you are ready to go.

### Deployment on an external webserver

#### Overview
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

#### Deploying the docker module

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
   sudo bash deploy.sh
```

The `deploy.sh` script will download the latest versions of the `hed-python`
and the `hed-web` repositories and deploy.

### Branches and versions

The web tools are built on the `hedtools` package housed in the `hed-python`
GitHub repository.
The tools are related to the `hed-specification` and `hed-schemas` repositories.
The branches correspond as follows:

| Branch |  Meaning | Synchronized with |
| ------ | -------- | ------------------ |
| stable | Tagged as a released version - will not change. | `stable@hed-python`<br/>`stable@hed-specification`<br/>`stable@hed-examples` |
| master | Most recent usable version.<br/>[https://hedtools/edu/hed](https://hedtools/edu/hed). | `master@hed-python`<br/>`master@hed-specification`<br/>`main@hed-examples` |
| develop | Experimental and evolving.<br/>[https://hedtools/edu/hed_dev](https://hedtools/edu/hed_dev). | `develop@hed-python`<br/>`develop@hed-specification`<br/>`develop@hed-examples` |

As features are integrated, they first appear in the `develop` branches of the
repositories.
The `develop` branches of the repositories will be kept in sync as much as possible
If an interface change in `hed-python` triggers a change in `hed-web` or `hed-examples`,
every effort will be made to get the `master`/`main` branches of the respective repositories in
sync.
The `stable` version refers to the last officially released version.
It generally refers to a version without the latest features.

API documentation is generated on ReadTheDocs when a new version is
pushed on any of the three branches. For example, the API documentation for the
`latest` branch can be found on [hed-python.readthedocs.io/en/latest/](hed-python.readthedocs.io/en/latest/). 

More information about using the webtools can be found at [https://www.hed-resources.org]([https://www.hed-resources.org]).
