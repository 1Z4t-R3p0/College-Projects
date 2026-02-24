#!/bin/bash
# WebGuard Setup Script for Mac and Linux
echo "------------------------------------------------"
echo "WebGuard Security Scanner - Setup & Run"
echo "------------------------------------------------"
if ! [ -x "$(command -v docker)" ]; then
  echo "Error: Docker is not installed. Please install Docker first: https://docs.docker.com/get-docker/"
  exit 1
fi
DOCKER_COMPOSE_CMD="docker compose"
if ! docker compose version > /dev/null 2>&1; then
    if ! [ -x "$(command -v docker-compose)" ]; then
        echo "Error: Docker Compose is not installed."
        exit 1
    else
        DOCKER_COMPOSE_CMD="docker-compose"
    fi
fi
$DOCKER_COMPOSE_CMD up --build -d
if [ $? -eq 0 ]; then
    echo "WebGuard is now running at http://localhost:8000"
else
    echo "Error: Failed to start."
fi
