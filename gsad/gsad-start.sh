#!/bin/sh
echo "starting gsad custome"
gsad --http-only -p 9393 --http-cors="http://localhost:9392"
tail -f /var/log/gvm/gsad.log