'''
Created on 27 dec. 2012

@author: ediemert
'''

import logging
from twisted.internet import reactor
import cyclone.web

from varan.ts_store import TSStore
from varan.monitor import Monitor
from twisted.internet.task import LoopingCall

class DefaultHandler(cyclone.web.RequestHandler):
    def initialize(self, store):
        self.store = store
    def get(self):
        try:
            self._get()
        except Exception as e:
            logging.error(e,exc_info=True)
            self.write('%s : %s'%(type(e),e))
            self.set_status(500)
        def _get(self):
            query = self.get_argument('q','#ratp')
            limit = int(self.get_argument('l','20'))
            results = self.store.retrieve(query, limit)
            timestamps = [ r[0] for r in results ]
            results = dict(results)
            results['timestamps'] = timestamps
            self.write(results)

class Application(cyclone.web.Application):
    def __init__(self, store):
        self.store = store
        handlers = [
                    (r"/", DefaultHandler, {'store':self.store}),
            ]
        cyclone.web.Application.__init__(self,
                                         handlers)

if __name__ == '__main__':
    store = TSStore()
    monitor = Monitor(['#ratp','#velib'], store)
    monitor_task = LoopingCall(monitor)
    monitor_task.start(30)
    reactor.listenTCP(6669, 
                      Application(store))
    reactor.run()
