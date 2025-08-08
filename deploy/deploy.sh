#!/bin/bash

# deploy.sh - Script to build and deploy a Docker container for the HEDTools online validator
# Usage: ./deploy.sh [branch] [environment]
# Environment can be 'prod' or 'dev' (defaults to 'prod')

##### Constants
BRANCH="${1:-master}"
ENVIRONMENT="${2:-prod}"
DEPLOY_DIR=$(pwd)

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

GIT_WEB_REPO_URL="https://github.com/hed-standard/hed-web"
GIT_WEB_REPO_BRANCH="$BRANCH"
CONTAINER_PORT=80

# Directory paths
GIT_HED_WEB_DIR="${DEPLOY_DIR}/hed-web"
CODE_DEPLOY_DIR="${DEPLOY_DIR}/hedtools"
SOURCE_DEPLOY_DIR="${GIT_HED_WEB_DIR}/deploy"
CONFIG_FILE="${CODE_DEPLOY_DIR}/config.py"

# Source files
BASE_CONFIG_FILE="${SOURCE_DEPLOY_DIR}/base_config.py"
SOURCE_DOCKERFILE="${SOURCE_DEPLOY_DIR}/Dockerfile"
SOURCE_REQUIREMENTS_FILE="${SOURCE_DEPLOY_DIR}/requirements.txt"
LOGROTATE_CONF_FILE="${SOURCE_DEPLOY_DIR}/gunicorn-logrotate.conf"
WEB_CODE_DIR="${GIT_HED_WEB_DIR}/hedweb"

##### Functions

# Print error message and exit
error_exit() {
    echo "[ERROR] $1"
    exit 1
}

# Clone the GitHub repository
clone_github_repos() {
    echo "Cloning repository ${GIT_WEB_REPO_URL} into ${DEPLOY_DIR} using branch ${GIT_WEB_REPO_BRANCH}..."
    git clone --branch "${GIT_WEB_REPO_BRANCH}" "${GIT_WEB_REPO_URL}" || error_exit "Failed to clone repo ${GIT_WEB_REPO_URL}"
}

# Create the necessary web directory structure and copy config files
setup_web_directory() {
    echo "Setting up web directory for ${ENVIRONMENT} environment..."
    mkdir -p "${CODE_DEPLOY_DIR}"
    cp "${BASE_CONFIG_FILE}" "${CONFIG_FILE}" || error_exit "Failed to copy base config file"
    cp "${SOURCE_DOCKERFILE}" "${DEPLOY_DIR}/Dockerfile" || error_exit "Failed to copy Dockerfile"
    cp "${SOURCE_REQUIREMENTS_FILE}" "${DEPLOY_DIR}/requirements.txt" || error_exit "Failed to copy requirements.txt"
    cp "${LOGROTATE_CONF_FILE}" "${DEPLOY_DIR}/gunicorn-logrotate.conf" || error_exit "Failed to copy ${LOGROTATE_CONF_FILE} to ${DEPLOY_DIR}/gunicorn-logrotate.conf"
    cp -r "${WEB_CODE_DIR}" "${CODE_DEPLOY_DIR}" || error_exit "Failed to copy web code"
}

# Build the Docker image
build_docker_image() {
    echo "Building Docker image ${IMAGE_NAME} for ${ENVIRONMENT} environment..."
    docker build --build-arg HED_INSTALL_SOURCE="${HED_INSTALL_SOURCE}" --build-arg CACHE_BUST="$(date +%s)" -t "${IMAGE_NAME}" . || error_exit "Failed to build Docker image"
}

# Stop and remove existing container
stop_existing_container() {
    echo "Stopping and removing existing container ${CONTAINER_NAME}..."
    docker stop "${CONTAINER_NAME}" 2>/dev/null || echo "Container ${CONTAINER_NAME} was not running"
    docker rm "${CONTAINER_NAME}" 2>/dev/null || echo "Container ${CONTAINER_NAME} did not exist"
}

# Run the Docker container
run_docker_container() {
    echo "Running Docker container ${CONTAINER_NAME} on port ${HOST_PORT}..."
    docker run -d \
        --name "${CONTAINER_NAME}" \
        -p "${HOST_PORT}:${CONTAINER_PORT}" \
        -e HED_URL_PREFIX="${URL_PREFIX}" \
        -e HED_STATIC_URL_PATH="${STATIC_URL_PATH}" \
        "${IMAGE_NAME}" || error_exit "Failed to run Docker container"
}

# Clean up deployment files
cleanup() {
    echo "Cleaning up deployment files..."
    rm -rf "${GIT_HED_WEB_DIR}" "${CODE_DEPLOY_DIR}" "Dockerfile" "requirements.txt" "gunicorn-logrotate.conf"
}

##### Main execution
echo "Starting deployment for ${ENVIRONMENT} environment..."
echo "Branch: ${GIT_WEB_REPO_BRANCH}"
echo "Image: ${IMAGE_NAME}"
echo "Container: ${CONTAINER_NAME}"
echo "Port: ${HOST_PORT}"

clone_github_repos
setup_web_directory
build_docker_image
stop_existing_container
run_docker_container
cleanup

echo "Deployment completed successfully!"
echo "Application is running at: http://localhost:${HOST_PORT}${URL_PREFIX}"
