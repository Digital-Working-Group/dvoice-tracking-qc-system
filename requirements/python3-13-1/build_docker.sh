#!/bin/bash
if [ $# -eq 1 ];
then
    docker_name=$1
else
    docker_name="qc-system-py-3-13-1"
fi
docker build -t $docker_name .