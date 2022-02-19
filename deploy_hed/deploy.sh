#!/bin/bash

# deploy.sh - A script used to _build and deploy a docker container for the HEDTools online validator

##### Constants

DEPLOY_DIR=${PWD}
IMAGE_NAME="hedtools:latest"
CONTAINER_NAME="hedtools"
GIT_WEB_REPO_URL="https://github.com/hed-standard/hed-web"
GIT_TOOLS_REPO_URL="https://github.com/hed-standard/hed-python"
GIT_HED_PYTHON_DIR="${DEPLOY_DIR}/hed-python"
GIT_HED_WEB_DIR="${DEPLOY_DIR}/hed-web"
GIT_WEB_REPO_BRANCH="master"
GIT_TOOLS_REPO_BRANCH="master"
HOST_PORT=33000
CONTAINER_PORT=80

CODE_DEPLOY_DIR="${DEPLOY_DIR}/hedtools"
SOURCE_DEPLOY_DIR="${DEPLOY_DIR}/hed-web/deploy_hed"
BASE_CONFIG_FILE="${SOURCE_DEPLOY_DIR}/base_config.py"
CONFIG_FILE="${CODE_DEPLOY_DIR}/config.py"
SOURCE_WSGI_FILE="${SOURCE_DEPLOY_DIR}/web.wsgi"
SOURCE_DOCKERFILE="${SOURCE_DEPLOY_DIR}/Dockerfile"
SOURCE_REQUIREMENTS_FILE="${SOURCE_DEPLOY_DIR}/requirements.txt"
SOURCE_HTTPD_CONF="${SOURCE_DEPLOY_DIR}/httpd.conf"
WEB_CODE_DIR="${DEPLOY_DIR}/hed-web/hedweb"
VALIDATOR_CODE_DIR="${DEPLOY_DIR}/hed-python/hed"

##### Functions

clone_github_repos(){
echo "Deploy dir: ${DEPLOY_DIR}"
cd ${DEPLOY_DIR}
echo "Cloning repo ${GIT_TOOLS_REPO_URL} in ${DEPLOY_DIR} using ${GIT_TOOLS_REPO_BRANCH} branch"
git clone $GIT_TOOLS_REPO_URL -b $GIT_TOOLS_REPO_BRANCH
echo "Cloning repo ${GIT_WEB_REPO_URL}  in ${DEPLOY_DIR} using ${GIT_WEB_REPO_BRANCH} branch"
git clone $GIT_WEB_REPO_URL -b $GIT_WEB_REPO_BRANCH
}

create_web_directory()
{
echo Creating hedweb directory...
echo "Make ${CODE_DEPLOY_DIR}"
mkdir "${CODE_DEPLOY_DIR}"
echo "Copy ${BASE_CONFIG_FILE} to ${CONFIG_FILE}"
cp "${BASE_CONFIG_FILE}" "${CONFIG_FILE}"
echo "Copy ${SOURCE_WSGI_FILE} to ${CODE_DEPLOY_DIR}"
cp "${SOURCE_WSGI_FILE}" "${CODE_DEPLOY_DIR}/."
echo "Copy ${SOURCE_DOCKERFILE} to ${DEPLOY_DIR}"
cp "${SOURCE_DOCKERFILE}" "${DEPLOY_DIR}/."
echo "Copy ${SOURCE_REQUIREMENTS_FILE} to ${DEPLOY_DIR}"
cp "${SOURCE_REQUIREMENTS_FILE}" "${DEPLOY_DIR}/."
echo "Copy ${SOURCE_HTTPD_CONF} to ${DEPLOY_DIR}"
cp "${SOURCE_HTTPD_CONF}" "${DEPLOY_DIR}/."
echo "Copy ${WEB_CODE_DIR} directory to ${CODE_DEPLOY_DIR}"
cp -r "${WEB_CODE_DIR}" "${CODE_DEPLOY_DIR}"
echo "Copy ${VALIDATOR_CODE_DIR} directory to ${CODE_DEPLOY_DIR}"
cp -r "${VALIDATOR_CODE_DIR}" "${CODE_DEPLOY_DIR}"
echo "Copy ${SOURCE_DEPLOY_DIR} directory to ${CODE_DEPLOY_DIR}"
cp -r "${VALIDATOR_CODE_DIR}" "${CODE_DEPLOY_DIR}"

}

switch_to_web_directory()
{
echo Switching to hedweb directory...
cd "${DEPLOY_DIR}" || error_exit "Cannot access $DEPLOY_DIR"
}

build_new_container()
{
echo "Building new container ${IMAGE_NAME} ..."
docker build -t $IMAGE_NAME .
}

delete_old_container()
{
echo "Deleting old container ${CONTAINER_NAME} ..."
docker rm -f $CONTAINER_NAME
}

run_new_container()
{
echo "Running new container $CONTAINER_NAME ..."
docker run --restart=always --name $CONTAINER_NAME -d -p 127.0.0.1:$HOST_PORT:$CONTAINER_PORT $IMAGE_NAME
}

cleanup_directory()
{
echo "Cleaning up directory ${GIT_HED_PYTHON_DIR} ..."
rm -rf "${GIT_HED_PYTHON_DIR}"
echo "Cleaning up directory ${GIT_HED_WEB_DIR} ..."
rm -rf "${GIT_HED_WEB_DIR}"
echo "Cleaning up ${CODE_DEPLOY_DIR}"
rm -rf ${CODE_DEPLOY_DIR}
}

error_exit()
{
	echo "$1" 1>&2
	exit 1
}

output_paths()
{
echo "The relevant deployment information is:"
echo "Deploy directory: ${DEPLOY_DIR}"
echo "Docker image name: ${IMAGE_NAME}"
echo "Docker container name: ${CONTAINER_NAME}"
echo "Git tools repo: ${GIT_TOOLS_REPO_URL}"
echo "Git web repo: ${GIT_WEB_REPO_URL}"
echo "Git web repo branch: ${GIT_WEB_REPO_BRANCH}"
echo "Git tools repo branch: ${GIT_TOOLS_REPO_BRANCH}"
echo "Git hed web dir: ${GIT_HED_WEB_DIR}"
echo "Host port: ${HOST_PORT}"
echo "Container port: ${CONTAINER_PORT}"
echo "Local deployment directory: ${DEPLOY_DIR}"
echo "Local deploy code dir: ${DEPLOY_CODE_DIR}"
echo "Local code deployment directory: ${CODE_DEPLOY_DIR}"
echo "Configuration file: ${CONFIG_FILE}"
echo "Base configuration file: ${BASE_CONFIG_FILE}"
echo "Source WSGI file: ${SOURCE_WSGI_FILE}"
echo "Source web code directory: ${WEB_CODE_DIR}"
echo "Source validator code directory: ${VALIDATOR_CODE_DIR}"
}

##### Main
echo "Starting...."
output_paths
echo "....."
# echo "Cleaning up directories before deploying..."
cleanup_directory
#if [ -z "$1" ]; then
#echo No branch specified... Using master branch
#else
#echo Branch specified... Using "$1" branch
#GIT_REPO_BRANCH="$1"
#fi
clone_github_repos || error_exit "Cannot clone repo ${GIT_TOOLS_REPO_URL} or ${GIT_WEB_REPO_URL}"
create_web_directory
switch_to_web_directory
build_new_container
delete_old_container
run_new_container
cleanup_directory
