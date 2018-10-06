du -hs /tmp
find /tmp -name '*.png' -type f -mmin +900 -delete
find /tmp -name '*.jpeg' -type f -mmin +900 -delete
find /tmp -name '*.jpg' -type f -mmin +900 -delete
find /tmp/* -type d -ctime +1 -exec rm -rf {} \;
echo 'done with /tmp/*.png *.jpeg *.jpg'
