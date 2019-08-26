#! /bin/bash

if [[ $# -ne 1 ]]; then
    echo "Usage: scheduler.sh <delay>"
    exit 1
fi

PDIR="programs"
PLAYERS="$PDIR/player1# $PDIR/player2# $PDIR/player3# $PDIR/player4# $PDIR/player5# $PDIR/player6# $PDIR/player7# $PDIR/player8#"

LAST_RUN=0
while true; do
    TIME=$(date +%s)
    if [[ $((TIME - LAST_RUN)) -ge $1 ]]; then
        NAME=$(date +%H%M)
        
        ./run.py $(echo $PLAYERS | sed s/#/.A.bin/g) -m empty -o frontend/logs/$NAME.A.log
        
        LAST_RUN=$TIME
    else
        sleep $(($1 - TIME + LAST_RUN))
    fi
done
