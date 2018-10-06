#!/bin/bash
echo $1 $2 $3
jarsigner -verbose -keystore /home/ubuntu/scewpt/etc/bin/apk/keystores/$1.jks -storepass Tererdfcv -keypass Tererdfcv /home/ubuntu/$1/$2/app/$3.apk $2