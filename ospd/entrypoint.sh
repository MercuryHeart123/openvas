#!/bin/sh
exec cron -f &
if [ "$(id -u)" = "0" ]; then
    echo "fixing volume permission"; echo
    # mkdir /var/lib/notus
    chown -R ospd-openvas /var/lib/notus
    chown -R ospd-openvas /var/lib/openvas
    # chown -R gvmd /var/lib/gvm
    exec gosu ospd-openvas "$@"
fi
echo "run as root"; echo
exec "$@"