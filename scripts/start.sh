#!/bin/bash
app="vosim_app"
docker stop ${app}
docker rm ${app}
docker build -t ${app} .
docker run -d -p 8050:8050 \
  --name=${app} \
  -v $PWD/app ${app}
