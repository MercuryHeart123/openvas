FROM greenbone/gsad
# WORKDIR /gsad
# COPY gsad/gsad-start.sh /gsad
# CMD ["bash","./gsad-start.sh"]
CMD echo "starting gsad custome"; gsad --http-only -p 9393 --http-cors="http://172.31.119.130:9392"; tail -f /var/log/gvm/gsad.log