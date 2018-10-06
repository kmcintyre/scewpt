#!/bin/bash
echo $1 $2 $3
/home/ubuntu/android-sdk-linux/build-tools/24.0.3/zipalign -f -v 4 /home/ubuntu/$1/$2/app/$3.apk /home/ubuntu/$1/$2/app/$3.zip.apk