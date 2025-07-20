#!/usr/bin/bash
# Gwyn Griffiths G3ZIL November 2024
# script to kill wsjtx job that is running, restart pulseaudio, then launch wsjtx
# this is to try and stop cumulative noise on WebSDR acquisition from browser for 24 GHz Kent installation
# Like all these websdr scripts it must be installed in directory jt4, usually in user home directory
# If needed this would be run once every * hours by cron
BASE_DIR=$(pwd)

# kill the wsjtx, having found out its process number
WSPR_PROC="$(ps -eLf | grep wsjtx | head -1 | awk '{print $2}')"
kill ${WSPR_PROC} > ${BASE_DIR}/pa_restart.log 2>&1

# restart pulseaudio. This is the key step to reducing audio problem growth
systemctl --user restart pulseaudio.service

# wait to be sure wsjtx has ended
sleep 2

# The browser and wsjtx will be running in a desktop GUI environment. We have to set the display here
# If you  have multiple screens, or using VNC, this may not be 0. Check if there is an error
export DISPLAY=":0.0"

# restart wsjtx - this is because restarting pulseaudio stops audio into wsjtx on restart
/usr/bin/wsjtx

echo "Done" >> ${BASE_DIR}/pa_restart.log
