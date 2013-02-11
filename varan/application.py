'''
Created on 2 janv. 2013

@author: ediemert
'''
import time

import cyclone.web
from cyclone.web import StaticFileHandler

from varan import logger

class DefaultHandler(cyclone.web.RequestHandler):
    def initialize(self, store):
        self.store = store
    def get(self):
        try:
            self._get()
        except Exception as e:
            logger.error(e,exc_info=True)
            self.write('%s : %s'%(type(e),e))
            self.set_status(500)
    def _get(self):
        query = self.get_argument('q','*')
        limit = int(self.get_argument('l','20'))
        results = self.store.retrieve(query, limit)
        self.write(results)

class Application(cyclone.web.Application):
    def __init__(self, store):
        self.store = store
        handlers = [
                    (r"/", DefaultHandler, {'store':self.store}),
                    (r"/web/(.*)", StaticFileHandler, {"path": 
                                                       "web"}),
            ]
        cyclone.web.Application.__init__(self,
                                         handlers)
    def log_request(self, handler):
        request_time = 1000.0 * handler.request.request_time()
        logger.info('HTTP %s %s %s (%.2f ms)',
                    handler._request_summary(),
                    handler.request.headers,
                    handler.get_status(),
                    request_time)