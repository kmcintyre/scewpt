from app import fixed, time_keys, user_keys
from amazon.dynamo import User

def bible_report(sr):    
    for index, league in enumerate(sr):
        print '{:3s}'.format(str(index+1)), '{:20s}'.format(league[user_keys.user_role]), 'since scraped:', fixed.lingo_since(league, time_keys.ts_bible)

if __name__ == '__main__':    
    leagues = User().get_leagues()
    leagues = sorted(leagues, key=lambda item: item[time_keys.ts_bible])        
    bible_report(leagues)