from app import keys
import os

round_corners_sizes = {
        'logo' : ('280x200', 'roundrectangle 0,0,280,200,20,20', '/tmp/logo.png'),
        'thumb' : ('48x48', 'roundrectangle 0,0,48,48,4,4', '/tmp/thumb.png'), 
        'small' : ('48x48', 'roundrectangle 0,0,48,48,4,4', '/tmp/small.png'), 
       'medium' : ('76x76', 'roundrectangle 0,0,76,76,6,6', '/tmp/medium.png'),
       'large' : ('210x210', 'roundrectangle 0,0,210,210,10,10', '/tmp/large.png'),
       'insta' : ('150x150', 'roundrectangle 0,0,150,150,8,8', '/tmp/insta.png'),
       'card' : ('290x281', 'roundrectangle 0,0,290,281,4,4', '/tmp/card.png'),
       }

social_keys = [keys.entity_twitter_id, keys.entity_twitter, keys.entity_facebook, keys.entity_wikipedia, keys.entity_instagram, keys.entity_linkedin, keys.entity_snapchat, keys.entity_match_twitter]

def round_corners(filepath, size):
    import subprocess    
    if not os.path.isfile(round_corners_sizes[size][2]):
        args = ['convert', '-size', round_corners_sizes[size][0], 'canvas:none', '-draw', round_corners_sizes[size][1], round_corners_sizes[size][2]]
        print 'command 1:', ' '.join(args)
        matte_create = subprocess.check_call(args)        
        print 'matte_create:', matte_create
    args2 = ['convert', filepath, '-matte', round_corners_sizes[size][2], '-compose', 'DstIn', '-composite', filepath]
    print 'command 2:', ' '.join(args2)
    round_corners_result = subprocess.check_call(args2)
    print 'round_corners_result:', round_corners_result    
