#!/bin/sh
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
echo "CRON: $(date +"%Y-%m-%d %T"): cronjob now updating CERT SCAP GVMD Feed" \
    >> /var/log/gvm/gvmd.log

gosu gvmd greenbone-feed-sync --type GVMD_DATA
gosu gvmd greenbone-feed-sync --type CERT
gosu gvmd greenbone-feed-sync --type SCAP \ 
    && echo "CRON: $(date +"%Y-%m-%d %T"): cronjob is finished update NVT Feed" \
    >> /var/log/gvm/gvmd.log
