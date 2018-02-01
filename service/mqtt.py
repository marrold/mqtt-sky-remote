from twisted.internet.defer import inlineCallbacks, DeferredList
from twisted.application.internet import ClientService, backoffPolicy
import service.sky as sky
from twisted.internet import reactor


class MQTTService(ClientService):

    name = 'mqtt-client'

    def __init__(self, endpoint, factory, config, log, connections):

        ClientService.__init__(self, endpoint, factory, retryPolicy=backoffPolicy())
        self.config = config
        self.log = log
        self.endpoint = endpoint
        self.connections = connections
        self.host = None
        self.port = None

    def log_retry(self):
        if 'mqtt-broker' not in self.connections:
            self.log.error("[MQTT] Connection timed out, will continue to retry in the background.")
            reactor.callLater(120, self.log_retry)

    def startService(self):
        # invoke whenConnected() inherited method
        reactor.callLater(10, self.log_retry)
        self.whenConnected().addCallback(self.connectToBroker)
        ClientService.startService(self)

    @inlineCallbacks
    def connectToBroker(self, protocol):

        self.protocol = protocol
        self.protocol.onPublish = self.onPublish
        self.protocol.onDisconnection = self.onDisconnection
        self.protocol.setWindowSize(3)
        self.host = self.protocol.transport.getPeer().host
        self.port = self.protocol.transport.getPeer().port

        try:
            yield self.protocol.connect("mqtt-sky-remote", username=self.config['MQTT']['USERNAME'], password=self.config['MQTT']['PASSWORD'], keepalive=60)
            yield self.subscribe()
        except Exception as e:
            self.log.error("[MQTT] Connecting to broker failed {%s!s}" % e)
            self.connections.pop(self.name, None)
        else:
            self.log.info("[MQTT] Connected and subscribed to broker")
            self.connections['mqtt-broker'] = 'connected'

    def subscribe(self):

        def _logFailure(failure):
            self.log.debug("[MQTT] Reported %s" % failure.getErrorMessage())
            return failure

        def _logGrantedQoS(value):
            return True

        def _logAll(*args):
            self.log.debug("[MQTT] All subscriptions complete")

        subslist = []

        for name in self.config['SKY_BOXES']:
            topic = ("sky/%s/send" % name)
            self.log.info("[MQTT] Subscribing to %s" % topic)
            sub = self.protocol.subscribe(topic, 2)
            sub.addCallbacks(_logGrantedQoS, _logFailure)
            subslist.append(sub)

        dlist = DeferredList(subslist, consumeErrors=False)
        dlist.addCallback(_logAll)
        return dlist

    def onPublish(self, topic, payload, qos, dup, retain, msgId):

        split_topic = topic.split("/")

        if split_topic[0] != 'sky' or split_topic[1] not in self.config['SKY_BOXES']:
            self.log.info("[MQTT] Received a message for an unsubscribed topic: %s" % topic)
        else:
            self.log.debug("[MQTT] Received a message for topic: %s" % topic)

        if split_topic[2] == 'send':
            self.target = split_topic[1]
            if self.target in self.connections:
                self.log.info("[SKY] (%s) Sending Command: %s." % (self.target, payload))
                sky.send_sky_command(self.log, self.target, self.connections[self.target], str(payload))
            else:
                self.log.info("[SKY] (%s) Box is offline. Unable to send the command %s" % (self.target, payload))


    def onDisconnection(self, reason):

        self.log.debug("[MQTT] <Connection was lost !> <reason={%s}>" % reason)
        self.connections.pop(self.name, None)
        self.whenConnected().addCallback(self.connectToBroker)

