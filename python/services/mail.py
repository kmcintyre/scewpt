from twisted.internet import reactor, defer

from services.smtp.cosner import MemoryBag, LastLoudestToS3, PerminentHtmlS3, PerminentJsonS3, Attachments, BagIt, CommandControl, CheckLockedAccount
from services.smtp.factory import ScewptSMTPServerFactory
from services.smtp.websocket import PostalScewptWSServerFactory

import time

smtp_port = 25
ws_port = 8080

def frontpage():
    from services.smtp import single_message_email
    from email.generator import Generator
    import StringIO

    print 'send frontpage:'

    from email.mime.text import MIMEText

    starup_info = 'System Start ' + \
        time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime())
    msg = MIMEText(starup_info)
    msg['subject'] = starup_info
    io = StringIO.StringIO()
    g = Generator(io, False)  # second argument means "should I mangle From?"
    g.flatten(msg)

    single_message_email.msg = io.getvalue()

    single_message_email.mailFrom = 'system-startup@127.0.0.1'
    single_message_email.mailTo = 'frontpage@localhost'
    single_message_email.send_messages('localhost', smtp_port)


def set_public_dns(postman_factory, failover=None):
    from twisted.web.client import getPage

    def set_localhost(err):
        print 'failover (None is don`t accept - accept from 127.0.0.1):', failover
        postman_factory.public_dns = failover

    def set_domain(domain):
        print 'set domain:', domain
        postman_factory.public_dns = domain
    d = getPage('http://169.254.169.254/latest/meta-data/public-hostname')
    d.addCallback(set_domain)
    d.addErrback(set_localhost)
    d.addCallback(lambda ign: defer.SUCCESS)

postman = PostalScewptWSServerFactory(url="ws://localhost:%s" % str(ws_port))
postman.bag = MemoryBag()
postman.routes.append(LastLoudestToS3())
postman.routes.append(PerminentHtmlS3())
postman.routes.append(PerminentJsonS3())
postman.routes.append(BagIt())
postman.routes.append(Attachments())
postman.routes.append(CommandControl())
postman.routes.append(CheckLockedAccount())


def startup():
    print 'started'
d = set_public_dns(postman)
smptfactory = ScewptSMTPServerFactory(postman=postman)

if __name__ == '__main__':
    reactor.listenTCP(ws_port, postman)
    reactor.listenTCP(smtp_port, smptfactory)

    print 'start smpt listener:', smtp_port
    print 'start cosner listener:', ws_port

    reactor.callLater(3.14, frontpage)
    reactor.run()

else:

    from twisted.application import internet, service
    application = service.Application("scewpt")

    multiservice = service.MultiService()

    ws_service = internet.TCPServer(ws_port, postman)
    stmp_service = internet.TCPServer(smtp_port, smptfactory)

    ws_service.setServiceParent(multiservice)
    stmp_service.setServiceParent(multiservice)

    print 'application set'
    multiservice.setServiceParent(application)
    reactor.callLater(3.14, frontpage)
