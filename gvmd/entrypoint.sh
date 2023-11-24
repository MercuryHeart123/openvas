#!/bin/sh
exec cron -f &
if [ "$(id -u)" = "0" ]; then
    echo "fixing volume permission"; echo
    chown -R gvmd /var/lib/gvm
    exec gosu gvmd "$@"
fi
echo "run as root"; echo
exec "$@"