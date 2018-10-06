from amazon.dynamo import User
from app import user_keys
import requests
import sys

league = sys.argv[1]
c = User().get_curator(league)

l = requests.get('http://' + c[user_keys.user_role] + '/' + league + '/db/bible.json').json()
popular = sorted(l, key = lambda k: len(k[league + '_mutual']) if league + '_mutual' in k else 0, reverse=True if len(sys.argv) > 2 else False)
for e in popular:
    try:
        n = e['name'].encode('ascii', 'ignore') if 'name' in e else e['profile'].split(':')[1].encode('ascii', 'ignore')
    except:
        n = 'not ascii'
    print 'name:', '{:40s}'.format(n), 'twitter:', '{:50s}'.format('https://twitter.com/' + e['twitter'] if 'twitter' in e else 'no twitter'), 'popularity:', '{:5s}'.format(str(len(e[league + '_mutual']) if league + '_mutual' in e else 0))
