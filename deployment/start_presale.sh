#!/bin/bash
set -e
LOGFILE=/home/presale/gunicorn.log
LOGDIR=$(dirname $LOGFILE)
NUM_WORKERS=2
# user/group to run as
USER=presale
GROUP=presale
cd /home/presale/c4sh_preorder
source ../presale/bin/activate
test -d $LOGDIR || mkdir -p $LOGDIR
exec ../presale/bin/gunicorn_django -w $NUM_WORKERS \
  --user=$USER --group=$GROUP --log-level=debug \
  --log-file=$LOGFILE 2>>$LOGFILE
