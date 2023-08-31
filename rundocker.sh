#!/bin/bash

# Build the Docker services
sudo docker-compose -f docker-compose-22.4.yml build

# Start the Docker services in detached mode
sudo docker-compose -f docker-compose-22.4.yml up -d
