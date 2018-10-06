import os
import boto.sqs
from twisted.internet import reactor
import time

from amazon import reboot

def get_number_of_tweets():
    
    c = boto.sqs.connect_to_region('us-east-1')
    q = c.create_queue('tweet')
    return int(q.get_attributes()['ApproximateNumberOfMessages'])

def do_check():
    tn = get_number_of_tweets()
    print 'tweet count:', tn
    if tn < 100:
        reactor.stop()
    else:
        stat = os.stat('/tmp/tweet_trim.html')
        print 'stats:', stat        
        file_mod_time = round(stat.st_mtime)
        difference = int(time.time()) - file_mod_time
        print 'file mod time:', file_mod_time, 'difference:', difference
        if difference > 600: 
            reactor.callLater(0, reboot.reboot, {'Tweets': tn})
        else:                
            reactor.stop()
    
if __name__ == '__main__':
    reactor.callLater(120, do_check)
    reactor.run()
