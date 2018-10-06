import os


def set_environment(video):
    print 'put video:', video
    if video:
        os.environ['VIDEO'] = video
    else:
        os.environ['VIDEO'] = "video.avi"
