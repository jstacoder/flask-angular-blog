web: bin/start-nginx gunicorn -k gevent\
         -t $TIMEOUT\
         --keep-alive $KEEPALIVE\
         --workers $WORKERS\                 
         $PRELOAD\
         --bind=unix:/tmp/nginx.socket\
         phlaskr:application
