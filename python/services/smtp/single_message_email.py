import StringIO
from email.generator import Generator
from email.mime.text import MIMEText
import os
from twisted.application import internet
from twisted.internet import protocol
from twisted.mail import smtp, relaymanager

mailFrom = "selfie@scewpt.com"
mailTo = "selfie@scewpt.com"

io = StringIO.StringIO()
g = Generator(io, False)
mt = MIMEText("blank msg")
g.flatten(mt)
msg = io.getvalue()


class SMTPTutorialClient(smtp.ESMTPClient):

    def __init__(self, secret, contextFactory=None, *args, **kw):
        smtp.ESMTPClient.__init__(self, secret, contextFactory, *args, **kw)

    def getMailFrom(self):
        return mailFrom

    def getMailTo(self):
        return [mailTo]

    def getMailData(self):
        return StringIO.StringIO(msg)

    def sentMail(self, code, resp, numOk, addresses, log):
        if self.factory.service[2] > numOk:
            print 'numOk:', numOk, self.factory.service[2]
            self.factory.service = (
                self.factory.service[0], self.factory.service[1], self.factory.service[2] - 1)
        else:
            try:
                self.factory.stopFactory()
                self.factory.service[0].stopService()
            except:
                pass

class SMTPClientFactory(protocol.ClientFactory):
    protocol = SMTPTutorialClient

    def __init__(self):
        self.service = None

    def buildProtocol(self, addr):
        print 'buildprotocol', addr
        p = self.protocol(secret=None, identity=self.service[1])
        p.factory = self
        return p

def getMailExchange(host):
    def cbMX(mxRecord):
        return str(mxRecord.name)
    return relaymanager.MXCalculator().getMX(host).addCallback(cbMX)


def cbMailExchange(exchange, port, repeate):
    print 'cb mail exchange', exchange
    smtpClientFactory = SMTPClientFactory()
    smtpClientService = internet.TCPClient(exchange, port, smtpClientFactory)
    smtpClientFactory.service = (smtpClientService, exchange, repeate)
    smtpClientService.startService()
    return smtpClientService


def send_messages(domain, port=25, repeate=1):
    d = getMailExchange(domain)
    d.addCallback(cbMailExchange, port, repeate)
    return d

if __name__ == '__main__':
    from twisted.internet import reactor

    def call_when_done(ans, repeate=0):
        print 'repeate:', ans, repeate
        if not repeate:
            print 'repeating:', (repeate - 1), 'more times'
            reactor.callLater(1, call_when_done, (repeate - 1))
        else:
            print 'stopping'

    def call_when_started(domain):
        d = send_messages(domain)
        d.addCallback(call_when_done, repeate=2)
    reactor.callWhenRunning(call_when_started, 'scewpt.com')
    reactor.run()
