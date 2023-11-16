#!/bin/sh

version=20230609.1
serviceName=registry.cn-hangzhou.aliyuncs.com/touchbiz/gas-client
targetTagName=$serviceName:$version


echo "begin to build image"
echo "[exec]: docker build -t $targetTagName -f Dockerfile ."
docker build --platform linux/amd64 -t $targetTagName .
# docker build --platform linux/arm64/v8 -t $targetTagName .
docker save -o ../gas-client-$version.tar $targetTagName

docker push $targetTagName

# docker stop touchbiz-pet

# docker rm touchbiz-pet 

# docker run -d --restart=always --name touchbiz-pet -p 80:80 $serviceName:$version

# docker start touchbiz-pet

# docker logs --tail=100 touchbiz-pet

