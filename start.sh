#!/bin/bash
gunicorn -k gevent\
         -t $TIMEOUT\
         --keep-alive $KEEPALIVE\
         --workers $WORKERS\
         $PID_ARG $APP_PID_FILE\
         $LOG_ARG $APP_LOG_FILE\
         $PRELOAD\
         --bind $PORT\
         phlaskr:application
