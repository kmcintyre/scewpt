from amazon.sqs import TweetQueue
from app import keys
import json
from twitter import twitter_keys

tq = TweetQueue()

while True:
    m = tq.getMessage()
    j = json.loads(m.get_body())
    print j[keys.entity_league]
    if j[keys.entity_league] in ['gov']:
        print 'delete'
        tq.deleteMessage(m)
    #print j[keys.entity_league], j.keys()
    #print j[keys.entity_league], j['message_tweet']
    '''
    if j[keys.entity_league] in ['golf','tennis'] and 'rank__change' in j: #'hollywood' and int(j['rank'].replace(',','')) > 500:
        f = int(j['rank__change'].split('__')[0])
        t = int(j['rank__change'].split('__')[1])
        print j[keys.entity_league], f, t
        if abs(f-t) < 7:
            print 'delete', j[keys.entity_league]
            tq.deleteMessage(m)        
    elif j[keys.entity_league] == 'gov':
        print 'delete', j[keys.entity_league]
        tq.deleteMessage(m)
    elif j[keys.entity_league] == 'hollywood':
        print 'keep:', j[keys.entity_league], j[twitter_keys.message_tweet]        
    else:
        print 'keep:', j[keys.entity_league]
    '''
    #if j[keys.entity_league] == 'gov':
    #    print 'delete', j[keys.entity_league]
    #    tq.deleteMessage(m)
