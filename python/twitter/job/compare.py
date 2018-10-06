import os
os.environ['QTDISPLAY'] = ':2'

from qt import qt5
print 'compare:', qt5.qt_version

from twisted.internet import reactor, task
import sys

def league_class(league_name):
    mod = __import__("league.scrape." + league_name, fromlist=[''])
    league = getattr(mod, league_name.upper())
    return league()

dry_run = False
if len(sys.argv) > 2:
    dry_run = True
    print 'dry run'

def runCompare(league_name):
    print 'runCompare'
    d = task.deferLater(reactor, 0, league_class(league_name).league_compare, False, dry_run)
    d.addCallback(lambda ign: reactor.stop())

if __name__ == '__main__': 
    reactor.callWhenRunning(runCompare, sys.argv[1])
    reactor.run()