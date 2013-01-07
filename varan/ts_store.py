'''
Created on 27 dec. 2012

@author: ediemert
'''
import time

from redis.client import Redis

from varan.tweet import Tweet

class TSStore(object):

    def __init__(self, config):
        self._redis = Redis(host=config.get('redis','host'), 
                            port=int(config.get('redis','port')),
                            db=int(config.get('redis','db')))
        self._delta_secs = int(eval(config.get('timeseries',
                                               'delta_secs')))
        self._expiration_delay_secs = int(eval(config.get('timeseries',
                                                          'expiration_delay_secs')))

    def _queries_key(self):
        return 'queries'
    @property
    def queries(self):
        return self._redis.smembers(self._queries_key())
    @queries.setter
    def queries(self, values):
        pipe = self._redis.pipeline()
        pipe.delete(self._queries_key())
        for v in values:
            pipe.sadd(self._queries_key(),
                      v)
        return pipe.execute()

    def _interval_key(self, timestamp):
        return int(timestamp) - int(timestamp) % self._delta_secs
    def _ts_key(self, timestamp, query):
        return 'ts:%(query)s:%(timestamp_key)s'%{'query':query,
                                                 'timestamp_key':self._interval_key(timestamp)}
    def _tweet_key(self, t):
        if type(t) == Tweet:
            return 'tweet:%s'%t.id
        return 'tweet:%s'%t
    def _query_key(self, query):
        return 'query:%s:last_tweet_id'%query

    def _store_tweet(self, pipe, tweet):
        tweet_key = self._tweet_key(tweet)
        pipe.set(tweet_key, tweet.serialize())
        pipe.expire(tweet_key, self._expiration_delay_secs)
    def _reference_tweet(self, pipe, timestamp, query, tweet):
        ts_key = self._ts_key(timestamp, query)
        pipe.lpush(ts_key,tweet.id)
        pipe.expire(ts_key,self._expiration_delay_secs)
    def _update_last_query_tweet(self, pipe, query, tweet):
        query_key = self._query_key(query)
        pipe.set(query_key,tweet.id)
    def append(self, query, tweet):
        pipe = self._redis.pipeline()
        timestamp = time.time()
        self._store_tweet(pipe, tweet)
        self._reference_tweet(pipe, timestamp, query, tweet)
        self._update_last_query_tweet(pipe, query, tweet)
        return pipe.execute()

    def retrieve_ts(self, query, timestamp, n_elements=-1):
        ts_key = self._ts_key(timestamp, query)
        return self._redis.lrange(ts_key, 0, n_elements)
    def retrieve_last_tweet_id(self, query):
        query_key = self._query_key(query)
        return self._redis.get(query_key)
    def retrieve_tweet(self, tweet_id):
        tweet_key = self._tweet_key(tweet_id)
        data = self._redis.get(tweet_key)
        return Tweet.deserialize(data).todict()
    def retrieve(self, query, n_periods=30):
        current_timestamp = now = int(time.time())
        start_timestamp = now - self._delta_secs * n_periods
        tweets = []
        while current_timestamp > start_timestamp:
            current_tweet_ids = self.retrieve_ts(query, current_timestamp)
            tweets.append({'timestamp': current_timestamp,
                           'tweets' : [ self.retrieve_tweet(tid) for tid in current_tweet_ids ] })
            current_timestamp -= self._delta_secs 
        return { 'now' : now,
                 'ts' : tweets }




