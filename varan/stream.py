# -*- coding: utf-8 -*-
'''
Created on 11 févr. 2013

@author: ediemert
'''
import time
from threading import Thread
import tweetstream
from varan import logger
from varan.tweet import Tweet

class Stream(Thread):

    def __init__(self, config, ts_store):
        self._queries = [ q.strip() for q in config.get('timeseries','queries').split(',') ]
        self.user_password = config.get('authentication','password').split(':')
        self.ts_store = ts_store
        self.wait_secs = 0
        self.last_wait = None
        self.should_stop = False
        Thread.__init__(self, target=self.__call__, 
                        name='StreamThread',
                        verbose=True)
        self.daemon = True

    @property
    def queries(self):
        return self.store._queries

    def update_wait(self, amount=0.5, factor=1, reset=False):
        if reset:
            self.wait_secs = 0
            self.last_wait = None
        else:
            self.wait_secs += amount
            self.wait_secs *= factor

    def stop(self):
        logger.info('stream thread stop called')
        self.should_stop = True
        Thread.join(self, timeout=1)

    def __call__(self):
        logger.info('stream thread main loop')
        while self.is_alive() and not self.should_stop:
            status = self.safe_listen()
            if status:
                if type(status) == StopIteration:
                    logger.warn('got stop loop message, exiting strem listener')
                    return
                logger.warn('got exception, will resume loop')

    def safe_listen(self):
        abnormal_exception = None
        try:
            self.listen_stream()
        except tweetstream.ReconnectImmediatelyError as rie:
            logger.error('got %s in stream: %s',
                         type(rie),
                         rie)
            self.update_wait()
        except tweetstream.ReconnectLinearlyError as rie:
            logger.error('got %s in stream: %s',
                         type(rie),
                         rie)
            self.update_wait(amount=1)
        except tweetstream.ReconnectExponentiallyError as rie:
            logger.error('got %s in stream: %s',
                         type(rie),
                         rie)
            self.update_wait(amount=1, factor=2)
        except Exception as e:
            logger.error('got abnormal exception in stream: %s',e,exc_info=True)
            abnormal_exception = e
        finally:
            if abnormal_exception:
                return abnormal_exception
            if self.last_wait and time.time() - self.last_wait > 15*60:
                logger.info('resetting time wait (last wait: %s)',
                            self.last_wait)
                self.update_wait(reset=True)
            self.last_wait = time.time()
            logger.info("will sleep %s secs",self.wait_secs)
            time.sleep(self.wait_secs)

    def listen_stream(self):
        with tweetstream.FilterStream(self.user_password[0], 
                                      self.user_password[1], 
                                      track=self._queries) as stream:
            for tweet_data in stream:
                tweet = Tweet.parse(tweet_data)
                self.ts_store.append('*',tweet)
                logger.info('got interesting tweet: %s', tweet)
                if self.should_stop or not self.is_alive():
                    logger.info('stop command detected')
                    break
        if self.should_stop or not self.is_alive():
            raise StopIteration('should stop now !')

if __name__ == '__main__':
    import sys, ConfigParser
    config = ConfigParser.ConfigParser()
    config.add_section('timeseries')
    config.set('timeseries','_queries',sys.argv[1])
    config.add_section('authentication')
    config.set('authentication','password',sys.argv[2])
    s = Stream(config, None)
    s.start()
