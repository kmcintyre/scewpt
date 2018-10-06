#!/bin/bash
sudo systemctl stop twitter_* league_* tweet_* services_* move_*
sudo systemctl disable twitter_* league_* tweet_* services_* move_*
  
sudo rm /etc/systemd/system/twitter_*.service
sudo rm /etc/systemd/system/league_*.service
sudo rm /etc/systemd/system/tweet_*.service
sudo rm /etc/systemd/system/services_*.service
sudo rm /etc/systemd/system/move_*.service
	
sudo swapoff /swapfile
sudo rm /swapfile
		
sudo truncate -s 0 /var/log/*.log
sudo truncate -s 0 /var/log/syslog
	
cd /home/ubuntu/scewpt
git pull
cd python

export PYTHONPATH=`pwd` 
python amazon/ami.py
