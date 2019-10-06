#!/bin/bash


ssh root@92.222.69.244 << HERE
ls /var/www/html
rm -r /var/www/html/vosim
ls /var/www/html
HERE

scp -rp /home/travis/build/kasztof/vosim root@92.222.69.244:/var/www/html

ssh root@92.222.69.244 "service apache2 restart"