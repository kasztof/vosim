#!/bin/bash
ssh root@92.222.69.244 rm -r /var/www/html/vosim
scp -rp /home/travis/build/kasztof/vosim root@92.222.69.244:/var/www/html
ssh root@92.222.69.244 cd /var/www/html/vosim
ssh root@92.222.69.244 cp /etc/vosim/.env .

ssh root@92.222.69.244 app="vosim_app"
ssh root@92.222.69.244 docker stop ${app}
ssh root@92.222.69.244 docker rm ${app}
ssh root@92.222.69.244 docker build -t ${app} .
ssh root@92.222.69.244 docker run -d -p 80:80 \
  --name=${app} \
  -v $PWD/app ${app}
