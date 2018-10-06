from qt import qt5
print 'avi_update:', qt5.qt_version

import sys
from amazon.dynamo import User, Entity, SocialBeta
from amazon import s3

from app import fixed
import pprint
import json

from PyQt5.QtQuick import QQuickView
from PyQt5.QtCore import QUrl

avi_property=[]
for e in Entity().query_2(index=Entity.index_team_profile,team__eq=sys.argv[1],query_filter={'twitter__null':False}):
    print e._data
    avi_property.append(e._data)


print avi_property

view = QQuickView() 
view.setSource(QUrl('qml/render/avi_team.qml'))
view.setWidth(590) 
view.setHeight(360)
view.rootObject().setProperty('avis', json.dumps(avi_property,cls=fixed.SetEncoder))
view.show()
print view.rootObject()
def screenshot():
    img = view.grabWindow();
    res = img.save('/home/ubuntu/Desktop/test.png')
    #res = img.save('/home/ubuntu/Desktop/avi_' + sys.argv[2] + '.png')
    print 'save result:', res    
#img = view.rootObject().grabToImage()
#print img 
from twisted.internet import task, reactor
task.deferLater(reactor, 10, screenshot).addCallback(lambda ign: qt5.signalDown(None, None))
reactor.run()