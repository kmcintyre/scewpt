#cd /usr/share/nginx
sites=( athleets bringwood d1tweets e2brute junkeet kotweet pokertalon redlinetweets ridertweet skintweet ventorta )
links=( polymer )
liblinks=( bower_components node_modules )
for i in "${sites[@]}"
do
	cd /usr/share/nginx
	if [ ! -d "$i" ]; then
		echo "nginx symlink $i"
		sudo ln -s ~/$i.com $i
	fi
	cd ~/$i.com
	for j in "${links[@]}"
	do
		if [ ! -d "$j" ]; then
			echo "folder symlink $i.com $j"
			ln -s ~/scewpt/$j $j
		fi	
	done
	for k in "${liblinks[@]}"
	do
		if [ ! -d "$k" ]; then
			echo "folder symlink $i.com $k"
			ln -s ~/scewpt/build/html/$k $k
		fi	
	done	
done
