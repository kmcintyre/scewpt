import os
os.environ['QTDISPLAY'] = ':2'
from qt import qt5
print 'scraper:', qt5.qt_version

from app import util

if __name__ == '__main__':
    import sys
    from twisted.internet import reactor
    l = util.league_class(sys.argv[1])
    print 'chrome_scrapper:', l.chrome_scraper    
    if l.chrome_scraper:
        print 'fresh:', l.chrome_fresh, 'width:', l.chrome_width, 'height:', l.chrome_height
        from qt.view import ChromeView
        cv = ChromeView(fresh=l.chrome_fresh)
        cv.setFixedWidth(l.chrome_width)
        cv.setFixedHeight(l.chrome_height)
        cv.show()
        l.cv = cv 
    reactor.callWhenRunning(l.process_league)  
    reactor.run()
