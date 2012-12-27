'''
Created on 27 dec. 2012

@author: ediemert
'''
from redis.client import Redis
import zlib
import datetime

class TSStore(object):

    def __init__(self):
        self._redis = Redis(db=1)
        self._delta = 20
        self._expiration_delay = 3600*24*1

    def _interval_key(self, timestamp):
        return timestamp - timestamp % self._delta
    def _ts_key(self, timestamp, query):
        return 'ts:%(query)s:%(timestamp_key)s'%{'query':query,
                                                 'timestamp_key':self._interval_key(timestamp)}
    def _tweet_key(self, tweet):
        return 'tweet:%d'%tweet.id
    def _query_key(self, query):
        return 'query:%s:last_tweet_id'%query

    def _store_tweet(self, pipe, tweet):
        tweet_key = self._tweet_key(tweet)
        pipe.setex(tweet_key, 
                   self._expiration_delay,
                   zlib.compress(tweet.serialize(),
                                 level=1))
    def _reference_tweet(self, pipe, timestamp, query, tweet):
        ts_key = self._ts_key(timestamp, query)
        pipe.lpush(ts_key,tweet.id)
        pipe.expire(ts_key,self._expiration_delay)
    def _update_last_query_tweet(self, pipe, query, tweet):
        query_key = self._query_key(query)
        pipe.set(query_key,tweet.id)
    def append(self, query, tweet):
        pipe = self._redis.pipeline()
        timestamp = datetime.datetime.now()
        self._store_tweet(pipe, tweet)
        self._reference_tweet(pipe, timestamp, query, tweet)
        self._update_last_query_tweet(pipe, query, tweet)
        return pipe.execute()

    def retrieve_ts(self, query, timestamp, n_elements):
        ts_key = self._ts_key(timestamp, query)
        return self._redis.lrange(ts_key, 0, n_elements)
    def retrieve_last_tweet_id(self, query):
        query_key = self._query_key(query)
        return self._redis.get(query_key)
    def retrieve(self, query, n_elements=30):
        timestamp = datetime.datetime.now()
        result = []
        while sum([ len(e[1]) for e in result ]) <= n_elements:
            result.insert(0, (timestamp,self.retrieve_ts(query, timestamp, n_elements)))
            if len(result[0][1]) == 0:
                break
            timestamp -= self._delta 
        return result
