#!/bin/bash
set -e
sudo gcloud auth print-access-token | sudo docker login -u oauth2accesstoken --password-stdin europe-west1-docker.pkg.dev
sudo docker pull europe-west1-docker.pkg.dev/arch-api-403919/arch-api-registry/arch-api:main
docker compose -f docker-compose-prod.yml up -d
