FROM greenbone/ospd-openvas
SHELL [ "/bin/bash", "-c" ]

RUN apt update && apt install -y \
    python3 \
    python3-pip \
    cron

RUN mkdir -p ${INSTALL_DIR}/greenbone-feed-sync
RUN python3 -m pip install \
    --root=${INSTALL_DIR}/greenbone-feed-sync \
    --no-warn-script-location greenbone-feed-sync
RUN cp -rv $INSTALL_DIR/greenbone-feed-sync/* /

COPY entrypoint.sh /
RUN chmod 777 /entrypoint.sh
COPY cronjob.sh /
RUN chmod 777 /cronjob.sh

RUN crontab -l | { cat; echo "0 */12 * * * bash /cronjob.sh"; } | crontab -
ENTRYPOINT ["/entrypoint.sh"]
CMD ospd-openvas -f \
    --config /etc/gvm/ospd-openvas.conf \
    --mqtt-broker-address mqtt-broker \
    --notus-feed-dir /var/lib/notus/advisories -m 666