#!/bin/bash

# deploy.sh - Script to build and deploy a Docker container for the HEDTools online validator

##### Constants
BRANCH="${1:-master}"
DEPLOY_DIR=$(pwd)
IMAGE_NAME="hedtools_dev:latest"
CONTAINER_NAME="hedtools_dev"
GIT_WEB_REPO_URL="https://github.com/hed-standard/hed-web"
GIT_WEB_REPO_BRANCH="$BRANCH"
HOST_PORT=33004
CONTAINER_PORT=80

# Directory paths
GIT_HED_WEB_DIR="${DEPLOY_DIR}/hed-web"
CODE_DEPLOY_DIR="${DEPLOY_DIR}/hedtools"
SOURCE_DEPLOY_DIR="${GIT_HED_WEB_DIR}/deploy_hed_dev"
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
    echo "Setting up web directory..."
    mkdir -p "${CODE_DEPLOY_DIR}"
    cp "${BASE_CONFIG_FILE}" "${CONFIG_FILE}" || error_exit "Failed to copy base config file"
    cp "${SOURCE_DOCKERFILE}" "${DEPLOY_DIR}/Dockerfile" || error_exit "Failed to copy Dockerfile"
    cp "${SOURCE_REQUIREMENTS_FILE}" "${DEPLOY_DIR}/requirements.txt" || error_exit "Failed to copy requirements.txt"
    cp "${LOGROTATE_CONF_FILE}" "${DEPLOY_DIR}/gunicorn-logrotate.conf" || error_exit "Failed to copy ${LOGROTATE_CONF_FILE} to ${DEPLOY_DIR}/gunicorn-logrotate.conf"
    cp -r "${WEB_CODE_DIR}" "${CODE_DEPLOY_DIR}" || error_exit "Failed to copy web code"
}

# Build a new Docker image
build_docker_image() {
    echo "Building Docker image ${IMAGE_NAME}..."
    docker build -t "${IMAGE_NAME}" . --build-arg CACHE_BUST=$(date +%s) || error_exit "Docker build failed"
}

# Stop and remove the old container if it exists
remove_old_container() {
    echo "Removing old container ${CONTAINER_NAME} if it exists..."
    docker rm -f "${CONTAINER_NAME}" &>/dev/null || echo "No existing container to remove"
}

# Run the new Docker container
run_new_container() {
    echo "Running new container ${CONTAINER_NAME}..."
    docker run --restart=always --name "${CONTAINER_NAME}" -d -p "127.0.0.1:${HOST_PORT}:${CONTAINER_PORT}" "${IMAGE_NAME}" || error_exit "Failed to start new Docker container"
}

# Clean up old directories
cleanup_directories() {
    echo "Cleaning up deployment directories..."
    rm -rf "${GIT_HED_WEB_DIR}" "${CODE_DEPLOY_DIR}" || error_exit "Failed to clean up directories"
}

# Print deployment details
output_deployment_info() {
    cat <<EOF
[INFO] Deployment Information:
- Deploy directory: ${DEPLOY_DIR}
- Docker image name: ${IMAGE_NAME}
- Docker container name: ${CONTAINER_NAME}
- Git repository URL: ${GIT_WEB_REPO_URL}
- Git branch: ${GIT_WEB_REPO_BRANCH}
- Host port: ${HOST_PORT}
- Container port: ${CONTAINER_PORT}
- Local code directory: ${CODE_DEPLOY_DIR}
- Configuration file: ${CONFIG_FILE}
EOF
}

##### Main Script

echo "[INFO] Starting deployment..."
output_deployment_info

echo "[INFO] Cleaning up old directories..."
cleanup_directories

echo "[INFO] Cloning GitHub repository..."
clone_github_repos

echo "[INFO] Setting up web directory..."
setup_web_directory

echo "[INFO] Building Docker image..."
build_docker_image

echo "[INFO] Removing old container..."
remove_old_container

echo "[INFO] Running new container..."
run_new_container

echo "[INFO] Cleaning up temporary directories..."
cleanup_directories

echo "[INFO] Deployment successful!"