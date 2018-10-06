scewpt
======

Core Compotents

STMP Server all MX complaint mail to S3
Twitter Contextual Streamer

I'm using 14.04 64-bit

security group should have SMTP/HTTP/WS/SSH open depending on purpose 

Note: enables remote systems Eclipse integration and non-cred login  

	ssh -i <key> ubuntu@ec2
	sudo adduser remoteuser
	sudo adduser remoteuser sudo
	# Edit allow
	sudo vi /etc/ssh/sshd_config
 	# Change to no to disable tunnelled clear text passwords - remember to set your security group for sshd
	PasswordAuthentication yes
	sudo restart ssh	
	exit

Note: system uses python boto for AWS calls.
	
	echo "[Credentials]" > .boto
	echo "aws_access_key_id = <key> " >> .boto
	echo "aws_secret_access_key = <pass>" >> .boto

Note: the script is an attempt to keep a latest/greatest version of Ubuntu install

    wget https://github.com/kmcintyre/scewpt/raw/master/scripts/ec2_install.sh
    chmod +x ec2_install.sh
    ./ec2_install.sh
    cd scewpt
    sudo twistd -noy scripts/quickstart.py
