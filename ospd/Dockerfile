FROM greenbone/ospd-openvas
SHELL [ "/bin/bash", "-c" ]
# ENV INSTALL_DIR=${HOME}/install
# RUN mkdir /home/ospd-openvas && chown ospd-openvas:ospd-openvas /home/ospd-openvas
# RUN chown -R ospd-openvas:ospd-openvas /var/lib/notus && chown -R ospd-openvas:ospd-openvas /var/lib/openvas/plugins
# RUN apt update && apt install   python3 \
#     python3-pip
RUN apt update && apt install -y \
    python3 \
    python3-pip \
    cron

RUN mkdir -p ${INSTALL_DIR}/greenbone-feed-sync
RUN python3 -m pip install --root=${INSTALL_DIR}/greenbone-feed-sync --no-warn-script-location greenbone-feed-sync
RUN cp -rv $INSTALL_DIR/greenbone-feed-sync/* /
# RUN cp -r ${HOME}/.local/bin /ospd-openvas
COPY entrypoint.sh /
RUN chmod 777 /entrypoint.sh
COPY cronjob.sh /
RUN chmod 777 /cronjob.sh
#update nvt feed every hour with  crontab
# RUN crontab -l | { cat; echo "*/5 * * * * echo cronjob update >> /var/log/gvm/ospd-openvas.log"; } | crontab -
RUN crontab -l | { cat; echo "0 */12 * * * bash /cronjob.sh"; } | crontab -
ENTRYPOINT ["/entrypoint.sh"]
CMD ospd-openvas -f --config /etc/gvm/ospd-openvas.conf --mqtt-broker-address mqtt-broker --notus-feed-dir /var/lib/notus/advisories -m 666
# ENV PATH="${PATH}:/home/ospd-openvas/.local/bin/"
