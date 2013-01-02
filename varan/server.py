# -*- coding: utf8 -*-
'''
Created on 27 dec. 2012

@author: ediemert
'''
import argparse
import ConfigParser
import os
import time

from twisted.internet import reactor

from varan import logger, VERSION
from varan.ts_store import TSStore
from varan.monitor import Monitor
from varan.application import Application

parser = argparse.ArgumentParser(description='varan : realtime twitter monitoring')
parser.add_argument('--config','-c', required=True)

if __name__ == '__main__':
    logger.info('-'*20+' varan v.%s '%VERSION+'-'*20)
    
    args = parser.parse_args()
    config = ConfigParser.ConfigParser()
    config.read(args.config)

    store = TSStore(config)
    store.queries = [ q.strip() for q in config.get('timeseries','queries').split(',') ]
    
    monitor = Monitor(config, store)
    monitor.start()
    
    reactor.listenTCP(int(config.get('ws', 'port')),
                      Application(store))
    reactor.run()
