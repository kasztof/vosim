#!/bin/bash

ssh root@92.222.69.244 << HERE
ls /var/www/html
rm -r /var/www/html/vosim
ls /var/www/html
HERE

scp -rp /home/travis/build/kasztof/vosim root@92.222.69.244:/var/www/html

ssh root@92.222.69.244 << HERE
cd /var/www/html/vosim
cp /etc/vosim/.env .
virtualenv -p python3 venv
source venv/bin/activate
pip3 install -r requirements.txt
deactivate
service apache2 restart
HERE