from twisted.internet import reactor
from twisted.python import log as twislog
from service.config import build_config
from twisted.internet.endpoints import clientFromString
from twisted.application import service
from mqtt.client.factory import MQTTFactory
import service.sky as sky
import service.mqtt as mqtt
import service.log_conf as log_conf

def startLogging():

    observer = twislog.PythonLoggingObserver(loggerName='mqtt-sky-remote')
    observer.start()

def make_service(config, log, connections, reactor=None):

    if reactor is None:
        from twisted.internet import reactor

    # create root service
    root = service.MultiService()

    # MQTT
    mqttFactory = MQTTFactory(profile=MQTTFactory.SUBSCRIBER)

    if config['MQTT']['TLS'] == True:
        uri = ('ssl:%s:%s' % (config['MQTT']['HOST'], config['MQTT']['PORT']))
        caCertsDir = "caCertsDir=%s" % config['MQTT']['CERTS']
        combined_endpoint = "%s:%s" % (uri, caCertsDir)
        log.debug("[MQTT] Attempting to connect to broker [%s]" % uri)

    else:
        uri = ('tcp:%s:%s' % (config['MQTT']['HOST'], config['MQTT']['PORT']))
        combined_endpoint = uri
        log.debug("[MQTT] Attempting to connect to broker [%s]" % uri)

    mqttEndpoint = clientFromString(reactor, combined_endpoint)

    mqttService = mqtt.MQTTService(mqttEndpoint, mqttFactory, config, log, connections)
    mqttService.setName('mqttService')
    mqttService.setServiceParent(root)

    # SKY
    for name in config['SKY_BOXES']:

        host = config['SKY_BOXES'][name]['HOST']
        port = 5900 if config['SKY_BOXES'][name]['SKY_Q'] is False else 49160
        uri = ('tcp:%s:%s' % (host, port))

        skyFactory = sky.ConnectionHandler(config, log, connections, name)
        skyEndpoint = clientFromString(reactor, uri)
        skyService = sky.SKYService(skyEndpoint, skyFactory, log, connections, name)
        skyService.setName(name)
        skyService.setServiceParent(root)

    return root


if __name__ == "__main__":

    config = build_config('mqtt-sky-remote.cfg')
    log = log_conf.config_logging(config['GLOBAL'])

    if config['GLOBAL']['LOG_TWISTED'] == True:
        log.debug("Twisted Logging Enabled")
        startLogging()

    connections = {}

    root = make_service(config, log, connections, reactor)
    application = service.Application('mqtt-sky-remote')
    root.setServiceParent(application)
    root.startService()

    reactor.run()
