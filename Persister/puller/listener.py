#message store

import hpfeeds
import logging


class Listener:
    def __init__(self, persister, ident, secret, port, host, feeds):
        self.logger = logging.getLogger()

        self.persister = persister

        self.ident = ident
        self.secret = secret
        self.port = port
        self.host = host
        self.feeds = feeds

    def start_listening(self):
        self.logger.debug('Trying to ')

        try:
            hpc = hpfeeds.new(self.host, self.port, self.ident, self.secret)
        except hpfeeds.FeedException, e:
            logging.error('Error: {0}'.format(e))

        def on_message(ident, chan, payload):
            self.persister.insert(ident, chan, payload)
            self.logger.debug('persisted message from {0} (payload size: {1})'
                .format(chan, len(payload)))

        def on_error(payload):
            logging.error('Error message from broker: {0}'.format(payload))
            hpc.stop()

        hpc.subscribe(self.feeds)
        try:
            hpc.run(on_message, on_error)
        except hpfeeds.FeedException, e:
            self.logger.error('Error: {0}'.format(e))
