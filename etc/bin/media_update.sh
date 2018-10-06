#!/bin/bash
gitprefix=kmcintyre
sites=(kotweet.com athleets.com bringwood.com d1tweets.com e2brute.com ventorta.com junkeet.com pokertalon.com skintweet.com redlinetweets.com ridertweet.com)
cd ~/
for var in "${sites[@]}"
  do
    if [ -d $var ]; then
      D=`echo $var | awk -F. '{print $1}'`
      cd /home/ubuntu/$var
      if [ ! -d html ]; then
      	echo $var 'found without html'
		ln -s ../scewpt/html html
      fi
      if [ ! -d script ]; then
        echo $var 'found without scripts'
        ln -s ../scewpt/script script
        cd /usr/share/nginx/
        sudo ln -s /home/ubuntu/$var $D
      fi
      cd /home/ubuntu/$var
      git pull
      cd ..
    else
      git clone https://github.com/$gitprefix/$var
      echo $var 'not found'
        fi
  done
