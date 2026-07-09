#!/bin/bash

# deploy.sh - Script to build and deploy a Docker container for the HEDTools online validator
# Usage: ./deploy.sh [branch] [environment] [bind_address]
# Environment can be 'prod' or 'dev' (defaults to 'prod')
# bind_address can be an IP like 0.0.0.0 (default) or 127.0.0.1 to restrict to localhost
#
# The script can be run from:
#   1. Inside the hed-server repo checkout (auto-detected, no clone needed)
#   2. A clean deploy directory (will clone from GitHub)
#   3. A directory with an existing hed-server/ subdirectory (reuses it)
#   4. With LOCAL_REPO set to copy from a local checkout:
#      LOCAL_REPO=/path/to/hed-server sudo bash deploy.sh main dev
#
# The Docker image is built directly from that repo checkout (deploy/Dockerfile
# is a multi-stage build: its first stage receives the full checkout, including
# .git, so setuptools-scm can compute hedweb's real version/commit; the final
# image only keeps the wheel that stage produces). That means this script does
# not need to assemble a separate build context by hand - it just points
# `docker build` at the repo directory.

##### Constants
BRANCH="${1:-main}"
ENVIRONMENT="${2:-prod}"
BIND_ADDRESS="${3:-0.0.0.0}"
DEPLOY_DIR=$(pwd)
RUNNING_IN_REPO=false

# Detect if we're running from inside the hed-server repo itself
if [ -d "${DEPLOY_DIR}/hedweb" ] && [ -d "${DEPLOY_DIR}/deploy" ] && [ -f "${DEPLOY_DIR}/pyproject.toml" ]; then
    RUNNING_IN_REPO=true
fi

# Set environment-specific variables
if [ "$ENVIRONMENT" = "dev" ]; then
    IMAGE_NAME="hedtools_dev:latest"
    CONTAINER_NAME="hedtools_dev"
    HOST_PORT=33004
    URL_PREFIX="/hed_dev"
    STATIC_URL_PATH="/hed_dev/hedweb/static"
    HED_INSTALL_SOURCE="main"
else
    IMAGE_NAME="hedtools:latest"
    CONTAINER_NAME="hedtools"
    HOST_PORT=33000
    URL_PREFIX="/hed"
    STATIC_URL_PATH="/hed/hedweb/static"
    HED_INSTALL_SOURCE="pypi"
fi

GIT_WEB_REPO_URL="https://github.com/hed-standard/hed-server"
GIT_WEB_REPO_BRANCH="$BRANCH"
CONTAINER_PORT=80

# The repo checkout that serves as the Docker build context
GIT_HED_SERVER_DIR="${DEPLOY_DIR}/hed-server"

##### Functions

# Print error message and exit
error_exit() {
    printf '[ERROR] %b\n' "$1" >&2
    exit 1
}

# Clone or locate the repository that will serve as the Docker build context
locate_repo() {
    if [ "${RUNNING_IN_REPO}" = true ]; then
        echo "Running from inside the hed-server repo at ${DEPLOY_DIR}..."
        GIT_HED_SERVER_DIR="${DEPLOY_DIR}"
        return 0
    fi

    if [ -d "${GIT_HED_SERVER_DIR}" ]; then
        echo "Using existing repository at ${GIT_HED_SERVER_DIR}..."
        return 0
    fi

    if [ -n "${LOCAL_REPO}" ]; then
        echo "Copying local repository from ${LOCAL_REPO} to ${GIT_HED_SERVER_DIR}..."
        cp -r "${LOCAL_REPO}" "${GIT_HED_SERVER_DIR}" || error_exit "Failed to copy local repo from ${LOCAL_REPO}"
        return 0
    fi

    echo "Cloning repository ${GIT_WEB_REPO_URL} into ${DEPLOY_DIR} using branch ${GIT_WEB_REPO_BRANCH}..."
    git clone --branch "${GIT_WEB_REPO_BRANCH}" "${GIT_WEB_REPO_URL}" "${GIT_HED_SERVER_DIR}" || error_exit "Failed to clone repo ${GIT_WEB_REPO_URL}.\nIf the network is unavailable, either:\n  1. Run this script from inside the hed-server repo checkout\n  2. Place the repo at ${GIT_HED_SERVER_DIR} before running this script\n  3. Place an existing hed-server/ subdirectory in the deploy directory\n  4. Set LOCAL_REPO=/path/to/hed-server to copy from a local checkout"
}

# Build the Docker image. The build context is the repo checkout itself
# (including .git) - deploy/Dockerfile's builder stage uses .git to let
# setuptools-scm compute hedweb's real version/commit, then the final image
# only copies the wheel that stage produces. See .dockerignore for what's
# trimmed out of the context (large/irrelevant local directories such as
# .venv/, __pycache__/, docs build output, etc. - .git is intentionally kept).
build_docker_image() {
    echo "Building Docker image ${IMAGE_NAME} for ${ENVIRONMENT} environment..."
    docker build \
        -f "${GIT_HED_SERVER_DIR}/deploy/Dockerfile" \
        --build-arg HED_INSTALL_SOURCE="${HED_INSTALL_SOURCE}" \
        --build-arg CACHE_BUST="$(date +%s)" \
        -t "${IMAGE_NAME}" \
        "${GIT_HED_SERVER_DIR}" \
        || error_exit "Failed to build Docker image"
}

# Stop and remove existing container
stop_existing_container() {
    echo "Stopping and removing existing container ${CONTAINER_NAME}..."
    docker stop "${CONTAINER_NAME}" 2>/dev/null || echo "Container ${CONTAINER_NAME} was not running"
    docker rm "${CONTAINER_NAME}" 2>/dev/null || echo "Container ${CONTAINER_NAME} did not exist"

    # Also free the host port regardless of container name. This matters
    # because "docker run -p" fails outright with "address already in use"
    # if *anything* is bound to HOST_PORT - not just a container named
    # ${CONTAINER_NAME}. That can happen if a previous run left a
    # differently-named or orphaned container behind (e.g. a cancelled CI
    # run that didn't get torn down in time), independent of whatever
    # caused the leftover container in the first place.
    local port_holders
    port_holders=$(docker ps -aq --filter "publish=${HOST_PORT}")
    if [ -n "${port_holders}" ]; then
        echo "Found other container(s) using host port ${HOST_PORT}, removing: ${port_holders}"
        docker rm -f ${port_holders} 2>/dev/null || true
    fi
}

# Resolve a GitHub token to forward into the container, without relying on
# shell environment inheritance (this repo's own docs tell people to run
# `sudo bash deploy.sh ...`, and `sudo` resets the environment by default -
# `export HED_GITHUB_TOKEN=...` in the caller's shell will NOT reach the
# script unless they specifically use `sudo -E` and their sudoers config
# allows it). Checked in order, first match wins:
#   1. HED_GITHUB_TOKEN / GITHUB_TOKEN env vars - works for a plain
#      (non-sudo) run, `sudo -E`, or CI, where env really is inherited.
#   2. deploy/.github_token next to this script, in the repo checkout that's
#      actually being deployed - a plain file read, unaffected by sudo. This
#      is the recommended option for a `sudo bash deploy.sh` setup: create it
#      once and every future deploy on that host picks it up automatically.
#   3. /etc/hed-server/github_token - a host-wide fallback for setups that
#      re-clone the repo on every deploy (so deploy/.github_token wouldn't
#      persist) but still want one token shared across environments on that
#      machine.
# Both files are read as-is and stripped of whitespace; neither is ever
# committed (see .gitignore for deploy/.github_token).
resolve_github_token() {
    local token="${HED_GITHUB_TOKEN:-${GITHUB_TOKEN}}"

    if [ -z "${token}" ] && [ -f "${GIT_HED_SERVER_DIR}/deploy/.github_token" ]; then
        token=$(tr -d '[:space:]' < "${GIT_HED_SERVER_DIR}/deploy/.github_token")
    fi

    if [ -z "${token}" ] && [ -f "/etc/hed-server/github_token" ]; then
        token=$(tr -d '[:space:]' < "/etc/hed-server/github_token")
    fi

    printf '%s' "${token}"
}

# Run the Docker container
run_docker_container() {
    echo "Running Docker container ${CONTAINER_NAME} on ${BIND_ADDRESS}:${HOST_PORT}..."

    # hedtools fetches HED schema versions from the GitHub API
    # (api.github.com) to populate the schema-version dropdown. Unauthenticated
    # requests are capped at 60/hour per source IP, which is easy to exhaust on
    # a shared/cloud host and causes that dropdown to silently fail to
    # populate (hedtools swallows the error and just returns what's already
    # cached). Passing a token raises the limit to 5000/hour - see
    # resolve_github_token() above for where it can come from. A fine-grained
    # GitHub PAT with no special scopes is enough; it's only used for
    # read-only API calls.
    local github_token_args=()
    local github_token
    github_token="$(resolve_github_token)"
    if [ -n "${github_token}" ]; then
        echo "Forwarding a GitHub token into the container for HED schema cache API calls..."
        github_token_args=(-e "HED_GITHUB_TOKEN=${github_token}")
    else
        echo "No GitHub token found (checked env vars, deploy/.github_token, /etc/hed-server/github_token) - schema cache API calls will be unauthenticated (60 requests/hour limit)."
    fi

    docker run -d \
        --name "${CONTAINER_NAME}" \
        -p "${BIND_ADDRESS}:${HOST_PORT}:${CONTAINER_PORT}" \
        -e HED_URL_PREFIX="${URL_PREFIX}" \
        -e HED_STATIC_URL_PATH="${STATIC_URL_PATH}" \
        "${github_token_args[@]}" \
        "${IMAGE_NAME}" || error_exit "Failed to run Docker container"
}

# Clean up deployment files
cleanup() {
    echo "Cleaning up deployment files..."
    if [ "${RUNNING_IN_REPO}" = false ]; then
        # Only remove the clone we made; do NOT touch anything when running
        # from inside an actual checkout (RUNNING_IN_REPO=true) or against a
        # pre-existing hed-server/ directory the caller provided.
        rm -rf "${GIT_HED_SERVER_DIR}"
    fi
}

##### Main execution
echo "Starting deployment for ${ENVIRONMENT} environment..."
echo "Branch: ${GIT_WEB_REPO_BRANCH}"
echo "Image: ${IMAGE_NAME}"
echo "Container: ${CONTAINER_NAME}"
echo "Port: ${HOST_PORT}"
echo "Bind address: ${BIND_ADDRESS}"

locate_repo
build_docker_image
stop_existing_container
run_docker_container
cleanup

echo "Deployment completed successfully!"
echo "Application is running at: http://localhost:${HOST_PORT}${URL_PREFIX}"
