ps -ef | grep gstreamer | wc -l
ps -ax | grep gstreamer | awk '{print $1}' | xargs kill -9
