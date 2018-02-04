from twisted.internet.protocol import Protocol, ClientFactory
from twisted.application.internet import ClientService
import string
import math
from twisted.internet import reactor

sky_commands = {
    'power': 0,
    'select': 1,
    'backup': 2,
    'dismiss': 2,
    'channelup': 6,
    'channeldown': 7,
    'interactive': 8,
    'sidebar': 8,
    'help': 9,
    'services': 10,
    'search': 10,
    'tvguide': 11,
    'home': 11,
    'i': 14,
    'text': 15,
    'up': 16,
    'down': 17,
    'left': 18,
    'right': 19,
    'red': 32,
    'green': 33,
    'yellow': 34,
    'blue': 35,
    '0': 48,
    '1': 49,
    '2': 50,
    '3': 51,
    '4': 52,
    '5': 53,
    '6': 54,
    '7': 55,
    '8': 56,
    '9': 57,
    'play': 64,
    'pause': 65,
    'stop': 66,
    'record': 67,
    'fastforward': 69,
    'rewind': 71,
    'boxoffice': 240,
    'sky': 241
}


def s_to_bytes(string):
    new_string = string.decode('ascii')
    new_string = new_string.rstrip("\n\r")

    if new_string.isprintable():
        return new_string
    else:
        new_string = ""
        for char in string:
            new_string = new_string + str(char).zfill(2)
        return new_string

def send_sky_command(log, target_name, target_endpoint, request):

    try:
        code = sky_commands[request]
        sky_buffer = bytearray([4, 1, 0, 0, 0, 0, int(math.floor(224 + (code / 16))), code % 16])
        target_endpoint.transport.write(bytes(sky_buffer))
        sky_buffer[1] = 0
        target_endpoint.transport.write(bytes(sky_buffer))

        log.debug("[SKY] (%s) Sending %s command successful." % (target_name, request))

    except:
        log.info("[SKY] (%s) Sending %s command failed." % (target_name, request))


class Login(Protocol):

    def __init__(self, config, log, connections, name):
        self.config = config
        self.log = log
        self.connections = connections
        self.name = name
        self.state = 'init-0'
        self.transport = None
        self.peer_ip = None

    def makeConnection(self, transport):
         self.transport = transport
         self.peer_ip = self.transport.getPeer()

    def connectionMade(self):
        self.log.info(" [SKY] (%s) Connected." % self.name)

    def connectionLost(self, reason):
        self.log.info(" [SKY] (%s) Connection lost." % self.name)
        self.connections.pop(self.name, None)

    def logPacket(self, data, state):
        self.log.debug('[SKY] (%s) Received: %s' % (self.name, s_to_bytes(data)))
        self.log.debug('[SKY] (%s) New State: %s' % (self.name, state))

    def dataReceived(self, data):

        if self.state == 'init-0':
            self.transport.write(data[0:24])
            self.state = 'init-1'
            self.logPacket(data, self.state)

        elif self.state == 'init-1':
            self.transport.write(data[0:1])
            self.state = 'init-2'
            self.logPacket(data, self.state)

        elif self.state == 'init-2':
            self.transport.write(data[0:1])
            self.state = 'init-3'
            self.logPacket(data, self.state)

        elif self.state == 'init-3':
            self.state = 'connected'
            self.logPacket(data, self.state)
            self.connections[self.name] = self
            self.log.info(" [SKY] (%s) Successfully logged in." % self.name)

            code = 255
            sky_buffer = bytearray([4, 1, 0, 0, 0, 0, int(math.floor(224 + (code/16))), code % 16])
            self.transport.write(bytes(sky_buffer))
            sky_buffer[1] = 0
            self.transport.write(bytes(sky_buffer))


class ConnectionHandler(ClientFactory):

    noisy = False

    def __init__(self, config, log, connections, name):
        self.config = config
        self.log = log
        self.connections = connections
        self.name = name
        self.peer_ip = None

    def buildProtocol(self, addr):
        self.peer_ip = addr
        self.log.debug('[SKY] (%s) Connection initiated.' % self.name)
        return Login(self.config, self.log, self.connections, self.name)

    def clientConnectionLost(self, connector, reason):
        self.log.info('[SKY] (%s) Lost connection. Reason: %s' % (self.name, reason))
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        self.log.info('[SKY] (%s) Connection failed. Reason: %s' % (self.name, reason))


class SKYService(ClientService):

    name = 'sky-client'

    def __init__(self, endpoint, factory, log, connections, name):
        ClientService.__init__(self, endpoint, factory)
        self.endpoint = endpoint
        self.factory = factory
        self.log = log
        self.connections = connections
        self.name = name

    def log_retry(self):

        if self.name not in self.connections:
            self.log.info(" [SKY] (%s) Connection timed out, will continue to retry in the background." % self.name)
            reactor.callLater(120, self.log_retry)

    def startService(self):
        reactor.callLater(10, self.log_retry)
        self.log.info(" [SKY] (%s) Attempting to connect." % self.name)
        ClientService.startService(self)
