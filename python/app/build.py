from amazon.dynamo import User
import pystache
from app import user_keys, fixed
from os.path import expanduser
import os
import sys
import json
import yaml
from shutil import copyfile
import subprocess

index_tmpl = open(expanduser("~") + '/scewpt/build/html/index.html', 'r').read()
    
commands = [['bower', 'install'], ['npm', 'install']]

for command in commands:
    subprocess.call(command, cwd=expanduser("~") + '/scewpt/build/html')

otherfiles = []
for item in os.listdir(expanduser("~") + '/scewpt/build/html/'):
    if item != 'index.html':
        if os.path.isfile(expanduser("~") + '/scewpt/build/html/' + item):
            otherfiles.append(item)

print 'other files:', otherfiles

for u in User().get_curators():        
    print 'build index:', u[user_keys.user_role]
    index_html = open(expanduser("~") + '/' + u[user_keys.user_role] + '/index.html', 'w')
    u[user_keys.user_site_leagues] = list(u[user_keys.user_site_leagues])
    u[user_keys.user_site_leagues].sort()
    #print u[user_keys.user_site_leagues], u[user_keys.user_site_leagues].__class__.__name__
    render_index = pystache.render(index_tmpl, yaml.load(json.dumps(u._data, cls=fixed.SetEncoder)))
    index_html.write(render_index) 
    index_html.close()        
    for f in otherfiles:
        src = expanduser("~") + '/scewpt/build/html/' + f
        dest = expanduser("~") + '/' + u[user_keys.user_role] + '/' + f
        print 'copy file:', dest        
        copyfile(src, dest)
    #for l in u[user_keys.user_site_leagues]:
        #league_file = expanduser("~") + '/scewpt/polymer/league/league-' + l + '.html'
        #if True or not os.path.isfile(expanduser("~") + '/scewpt/polymer/league/league-' + l + '.html'):
        #    print 'create leauge element:', l
        #    league_html = open(expanduser("~") + '/scewpt/polymer/league/league-' + l + '.html', 'w')
        #    render_league = pystache.render(league_tmpl, { 'league': l, 'capitalized_league': l.capitalize()})
        #    league_html.write(render_league)
        #    league_html.close()
    if len(sys.argv) > 1:
        subprocess.call(['polymer', 'build'], cwd=expanduser("~") + '/' + u[user_keys.user_role]) 
         
