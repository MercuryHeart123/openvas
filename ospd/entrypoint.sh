#!/bin/sh
exec cron -f &
if [ "$(id -u)" = "0" ]; then
    echo "fixing volume permission"; echo
    chown -R ospd-openvas /var/lib/notus
    chown -R ospd-openvas /var/lib/openvas
    exec gosu ospd-openvas "$@"
fi
echo "run as root"; echo
exec "$@"