#!/bin/bash

# Build Docker images
docker build -t datos -f Datos/Dockerfile .
docker build -t miembro1 -f Miembro1/Dockerfile .
docker build -t miembro2 -f Miembro2/Dockerfile .
docker build -t miembro3 -f Miembro3/Dockerfile .
docker build -t servidor -f Servidor/Dockerfile .


