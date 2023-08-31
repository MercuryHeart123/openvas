#!/bin/sh
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
echo "CRON: $(date +"%Y-%m-%d %T"): cronjob now updating NVT Feed $(whoami)" >> /var/log/gvm/ospd-openvas.log
gosu ospd-openvas greenbone-nvt-sync && echo "CRON: $(date +"%Y-%m-%d %T"): cronjob is finished update NVT Feed" >> /var/log/gvm/ospd-openvas.log
