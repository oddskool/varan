# -*- coding: utf8 -*-
'''
Created on 27 dec. 2012

@author: ediemert
'''
import argparse
import ConfigParser

from twisted.internet import reactor

from varan import logger, VERSION
from varan.ts_store import TSStore
from varan.stream import Stream
from varan.application import Application
from twisted.internet.threads import deferToThread

parser = argparse.ArgumentParser(description='varan : realtime twitter monitoring')
parser.add_argument('--config','-c', required=True)
parser.add_argument('--user','-u', required=True)

if __name__ == '__main__':
    import sys
    
    logger.info('-'*20+' varan v.%s '%VERSION+'-'*20)
    
    args = parser.parse_args()
    config = ConfigParser.ConfigParser()
    config.read(args.config)
    config.add_section('authentication')
    config.set('authentication', 'password', args.user)

    store = TSStore(config)
    store.queries = [ q.strip() for q in config.get('timeseries','queries').split(',') ]

    stream = Stream(config, store)

    try:
        #deferToThread(stream.__call__)
        stream.start()
        logger.info('stream listen started @main')
        reactor.listenTCP(int(config.get('ws', 'port')),
                          Application(store))
        logger.info('reactor will start @main')
        reactor.run()
    except KeyboardInterrupt:
        logger.critical('got ctrl+c, quit')
        stream.stop()
        logger.critical('got ctrl+c, quit (2)')
        reactor.stop()
        logger.critical('got ctrl+c, quit (3)')
        sys.exit(0)
