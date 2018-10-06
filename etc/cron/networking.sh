#!/bin/bash
GOOGLE_DSN=8.8.8.8
x=`ping -c1 $GOOGLE_DSN 2>&1 | grep unknown`
if [ ! "$x" = "" ]; then
        echo "It's down!! Attempting to restart."
        service network restart
fi