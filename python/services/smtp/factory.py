"""
A "email service" that:
    
    * tracks connections/command in dynamodb
    * writes messages to s3
    * rebroadcasts redis pub/sub 

Then re-broadcasting via www.amazon.com/mail and services://mail.amazon.com
"""

from autobahn.twisted.websocket import WebSocketClientFactory, WebSocketClientProtocol
from email import parser
import json
from twisted.internet import error
from twisted.mail import smtp
from zope.interface import implements

class ScewptMessageDelivery:
    implements(smtp.IMessageDelivery)

    def __init__(self, postman):
        self.postman = postman
        self.email_element = None

    def receivedHeader(self, helo, origin, recipients):
        print 'receivedHeader'
        if len(recipients) <> 1:
            raise "fuck this"
        self.email_element = self.postman.anticipate(
            helo, origin, recipients[0])

    def validateFrom(self, helo, origin):
        print "validateFrom:", helo, origin
        return origin

    def validateTo(self, user):
        print "validateTo:", user
        if str(user) in ['mg@scewpt.com', 'simon.longworth@bringwood.com']:
            raise smtp.SMTPBadRcpt(user)
        if user.dest.domain in self.postman.valid_domains:
            def emailcallback(incoming):
                return self.postman.new_email(incoming, self.email_element, user.dest.domain)
            return lambda: ScewptMessage(emailcallback)
        elif user.dest.domain in self.postman.invalid_domains:
            raise smtp.SMTPBadRcpt(user)
        else:
            def handleCheckDomain(isvalid):
                print 'isvalid:', isvalid, user.dest.domain
                if isvalid or user.dest.domain == 'localhost':
                    self.postman.valid_domains.append(user.dest.domain)
                else:
                    self.postman.invalid_domains.append(user.dest.domain)
            d = self.postman.check_domain(user.dest.domain)
            d.addBoth(handleCheckDomain)
            d.addBoth(lambda ign: self.validateTo(user))
            return d


class ScewptMessage:
    implements(smtp.IMessage)

    def __init__(self, finished=None):
        self.parser = parser.FeedParser()
        self.finished = finished

    def lineReceived(self, line):
        self.parser.feed(line + '\n')

    def eomReceived(self):
        print "message received: set data and dest file"
        if self.finished:
            return self.finished(self.parser.close())


class ScewptSMTPProtocol(smtp.ESMTP):

    def connectionMade(self):
        print 'connectionMade'

        smtp.ESMTP.connectionMade(self)

    def state_COMMAND(self, line):
        line = line.strip()

        parts = line.split(None, 1)
        if parts:
            method = self.lookupMethod(parts[0]) or self.do_UNKNOWN
            if len(parts) == 2:
                method(parts[1])
            else:
                method('')
        else:
            self.sendSyntaxError()

    def connectionLost(self, reason):
        if not reason.check(error.ConnectionDone):
            print 'connectionLost', reason
        smtp.SMTP.connectionLost(self, reason)

    def do_SCRB(self, url):
        if self.factory.postman and self.factory.postman.scribe:
            self.scrb = url
            self.sendCode(250, 'SCRB:' + url)
        else:
            self.sendCode(451, 'Scribe Not Enabled')

    def do_NEXT(self, nxt):
        if self.factory.postman and self.factory.postman.scribe:
            self.next = nxt
            self.sendCode(250, 'NEXT:' + nxt)
        else:
            self.sendCode(451, 'Next Not Enabled')

    def do_WSPP(self, nxt):
        if self.factory.postman and self.factory.postman.scribe:
            self.next = nxt
            self.sendCode(250, 'NEXT:' + nxt)
        else:
            self.sendCode(451, 'Next Not Enabled')

    def do_QUIT(self, rest):
        self.sendCode(221, 'Bye')
        self.transport.loseConnection()

class ScewptSMTPServerFactory(smtp.SMTPFactory):
    protocol = ScewptSMTPProtocol

    def __init__(self, postman, portal=None):
        smtp.SMTPFactory.__init__(self, portal)
        self.postman = postman

    def buildProtocol(self, addr):
        print 'buildProtocol:', addr.host
        p = smtp.SMTPFactory.buildProtocol(self, addr.host)
        if self.postman:
            p.host = self.postman.public_dns
        p.delivery = ScewptMessageDelivery(self.postman)
        p.canStartTLS = True
        return p


class ScewptWSClientProtocol(WebSocketClientProtocol):

    def route_email(self, ee):
        print 'client new_email:', ee.broadcast_dict
        self.sendMessage(json.dumps(ee.broadcast_dict))

    def status(self):
        self.sendMessage(json.dumps(self.postman.status()))
        reactor.callLater(120, self.status)

    def onOpen(self):
        print 'send server message'
        reactor.callLater(0, self.status)

    def connectionMade(self):
        print 'client connection made'
        WebSocketClientProtocol.connectionMade(self)
        self.postman.routes.append(self)

    def connectionLost(self, reason):
        print 'client connection made'
        self.postman.routes.remove(self)
        WebSocketClientProtocol.connectionLost(self, reason)

    def __repr__(self):
        return 'server-side websocket client'

class ScewptWSClientFactory(WebSocketClientFactory):
    protocol = ScewptWSClientProtocol

    def __init__(self, postman, url):
        WebSocketClientFactory.__init__(self, url)
        self.postman = postman

    def buildProtocol(self, addr):
        print 'build client protocol'
        p = WebSocketClientFactory.buildProtocol(self, addr.host)
        p.postman = self.postman
        return p
