echo "[Credentials]" > .boto
echo "aws_access_key_id = <key> " >> .boto
echo "aws_secret_access_key = <pass>" >> .boto

# sudo vi /etc/environment # append the following 2 lines
# LC_ALL=en_US.UTF-8
# LANG=en_US.UTF-8

sudo apt-get update

sudo apt-get -y install alsa-base ant fonts-takao fonts-thai-tlwg gcc git glances imagemagick libfreetype6-dev libgles2-mesa-dev libjpeg-dev libmagickwand-dev libnss3 libgl1-mesa-dev libssl-dev libx11-dev libx11-xcb-dev libxcb-glx0-dev libxcb1-dev libxext-dev libxfixes-dev libxi-dev libxrender-dev libxslt1-dev monit nginx python-dev python-lxml python-opencv python-pip python-setuptools unzip xvfb
	
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 2930ADAE8CAF5059EE73BB4B58712A2291FA4AD5
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.6 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.6.list 

sudo apt-get update
sudo apt-get install -y mongodb-org
cd /lib/systemd/system/
sudo systemctl enable mongod.service	

sudo pip install --upgrade pip
sudo pip install --upgrade websocket-client qtawesome autobahn BeautifulSoup4 boto cssselect jinja2 lxml oauth2 Pillow pyopenssl python-crontab python-levenshtein requests requests_oauthlib service_identity simplejson Twisted Wand psutil pymongo pystache pandas numpy
	 
#curl -sL https://deb.nodesource.com/setup_7.x | sudo -E bash -
#sudo apt-get install -y nodejs

#wget https://dl.google.com/android/repository/sdk-tools-linux-3859397.zip
#wget https://dl.google.com/android/repository/android-ndk-r14b-linux-x86_64.zip

git clone https://github.com/kmcintyre/scewpt

cd scewpt
git config credential.helper 'store'

sudo cp etc/systemd/xvfb.service /etc/systemd/system
sudo cp etc/systemd/swap.service /etc/systemd/system
sudo cp etc/systemd/media.service /etc/systemd/system
sudo cp etc/systemd/self_identify.service /etc/systemd/system
	
cd /etc/systemd/system/

sudo systemctl enable xvfb
sudo systemctl enable swap
sudo systemctl enable media
sudo systemctl enable self_identify

sudo systemctl start xvfb
sudo systemctl start swap
sudo systemctl start media

cd

sudo cp etc/nginx/site-enabled/default /etc/nginx/site-enabled/

wget http://download.qt.io/official_releases/qt/5.10
chmod +x qt-opensource-linux-x64-
export DISPLAY=:2
./qt-opensource-linux-x64-5.10.1.run --script ~/scewpt/etc/bin/ami/qt.install.js

wget https://www.riverbankcomputing.com/static/Downloads/sip/
python configure.py
make
sudo make install
cd ..

wget https://www.riverbankcomputing.com/static/Downloads/PyQt5/
python configure.py --qmake= 
make
sudo make install
cd ..