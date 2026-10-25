# Deployment files

What is in this directory and how the Docker image chooses its hedtools. The full procedure is in [docs/deployment.md](../docs/deployment.md).

## Usage

```bash
sudo bash deploy.sh main prod
```

`sudo bash deploy.sh [branch] [environment] [bind_address]` - three positional arguments, all optional:

1. **branch** (default `main`): the **hed-server** branch to clone and build. It is used only when the script clones from GitHub. When the script runs from inside a hed-server checkout, finds an existing `hed-server/` directory next to it, or is given `LOCAL_REPO=/path/to/hed-server`, that code is built as is and the branch argument is ignored.
2. **environment** (default `prod`): `prod` or `dev`. It selects two things:
   - where **hedtools** comes from: `prod` installs the released `hedtools>=1.3.0` from PyPI; `dev` installs hed-python's main branch from GitHub, reinstalled every build.
   - the container: `prod` runs `hedtools` on host port 33000 at `/hed`; `dev` runs `hedtools_dev` on host port 33004 at `/hed_dev`.
3. **bind_address** (default `0.0.0.0`): the host address the container port is published on; `127.0.0.1` restricts it to localhost.

The branch and the environment are independent: the branch never affects which hedtools is installed, and the environment never affects which hed-server branch is built. Examples:

```bash
sudo bash deploy.sh main prod             # hed-server main, hedtools from PyPI
sudo bash deploy.sh develop dev           # hed-server develop, hedtools from hed-python main
sudo bash deploy.sh main prod 127.0.0.1   # as the first, published on localhost only
```

## Files

- `deploy.sh` - builds the image and runs the container, as above.
- `Dockerfile` - a two-stage build. Stage 1 builds the hedweb wheel from the checkout (it needs `.git` for the version); stage 2 installs the wheel and its dependencies, then hedtools from the chosen source, then copies `base_config.py` to `/root/config.py`.
- `base_config.py` - the configuration the image runs with; environment variables override it.
- `gunicorn-logrotate.conf` - log rotation for the gunicorn access log.

## Where hedtools comes from

`HED_INSTALL_SOURCE` selects the hedtools install in stage 2:

| Value      | Used by                   | Installs                                             |
| ---------- | ------------------------- | ---------------------------------------------------- |
| `pypi`     | `deploy.sh <branch> prod` | `hedtools>=1.3.0` from PyPI (the default)            |
| `git-main` | `deploy.sh <branch> dev`  | hed-python main from GitHub, reinstalled every build |

`deploy.sh` passes a changing `CACHE_BUST`, and the Dockerfile references it in the wheel-install layer as well as in the hedtools layer, so neither is served from the layer cache: production picks up the latest hedtools release that satisfies `pyproject.toml`, and dev reinstalls the latest hed-python main.
