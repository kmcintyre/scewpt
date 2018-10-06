import boto.sqs
from boto.sqs.message import Message
import json

from app import keys
from app.fixed import SetEncoder

class Queue(object):    
    
    conn = boto.sqs.connect_to_region('us-east-1')
    
    def __init__(self, league = None):
        self.league = league
        
    def getConnection(self):
        return self.conn
    
    def queueName(self):
        return self.queue_name if self.league is None else self.queue_name + '_' + self.league
    
    def queueExists(self):
        qn = self.queueName()
        if self.conn.get_queue(qn):
            return True
        else:
            return False
        
    def deleteQueue(self):
        if self.getQueue().count() == 0:
            print 'delete queue'
            self.conn.delete_queue(self.getQueue())
    
    def getQueue(self):
        if not self.queueExists():
            self.conn.create_queue(self.queueName())
        return self.conn.get_queue(self.queueName())

    def createMessage(self, json_message):
        m = Message()
        m.set_body(json.dumps(json_message,cls=SetEncoder))
        self.getQueue().write(m)        

    def deleteMessage(self, message):
        self.getQueue().delete_message(message)        
        
    def getMaxMessages(self):
        cnt = self.getQueue().count()
        cnt = cnt if cnt < 10 else 10
        if cnt:
            return self.getQueue().get_messages(cnt, visibility_timeout=900)

    def getMessage(self):
        try:
            return self.getQueue().get_messages(1)[0]
        except:
            print 'missing messages:', self.queue_name, 'league:', self.league

class DeleteQueue(Queue):
    
    queue_name = 'delete'

class AvatarQueue(Queue):
    
    queue_name = 'avatar'
    
class BackgroundQueue(Queue):
    
    queue_name = 'background'

class TweetQueue(Queue):
    
    queue_name = 'tweet'
    
class BackupQueue(Queue):
    
    queue_name = 'backup'
    
class RecoverQueue(Queue):
    
    queue_name = 'recover'

class StalkQueue(Queue):
    
    queue_name = 'stalk'    
    
class ArchiveQueue(Queue):
    
    queue_name = 'archive'        
    
class WorkerQueue(Queue):
    
    queue_name = 'worker'