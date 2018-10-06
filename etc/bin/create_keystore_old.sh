#!/bin/bash
echo $1 $2
pass=Tererdfcv
keystore=/home/ubuntu/scewpt/etc/bin/apk/keystores/$1.jks
alias keycommand=`keytool -genkey -noprompt -keyalg RSA -keysize 2048 -validity 10000 -alias $2 -dname "CN=Argyle James, OU=$2, O=$1, L=Palo Alto, ST=CA, C=US" -keystore $keystore -storepass $pass -keypass $pass`
if [ ! -f $keystore ]; then
    echo "create keystore: $keystore"
	keycommand			     
fi
alias_count=$( keytool -list -v -noprompt -keystore $keystore -alias $2 -storepass $pass | grep "Alias <$2> does not exist" | wc -l )
echo "alias count: $alias_count"
if [[ $alias_count -ne "0" ]]; then
	keycommand		
fi