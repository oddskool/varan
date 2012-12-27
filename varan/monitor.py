'''
Created on 27 dec. 2012

@author: ediemert
'''
import json
import time
from operator import itemgetter

from twisted.internet import defer
from cyclone.httpclient import fetch as cyclone_fetch

from varan import VERSION, logger
from varan.tweet import Tweet
import urllib

class FetchException(Exception): pass

class Monitor(object):

    def __init__(self, queries, store):
        self.url_base = 'https://search.twitter.com/search.json'
        self.first_query_url = '%s?q=%%(query)s&result_type=mixed&count=1&include_entities=1' % self.url_base
        self.update_query_url = '%s?q=%%(query)s&result_type=mixed&since_id=%%(last_tweet_id)s&include_entities=1' % self.url_base
        self.headers = { 'Connection':['close'],
                         'Accept':['application/json'],
                         'User-Agent':['varan %s - https://github.com/oddskool/varan - contact: oddskool+varan@gmail.com'%VERSION] }
        self.queries = queries
        self.store = store

    def handle_response(self, query, url, response, recurse=True):
        logger.info('url: %s => response: %s', url, response.code)
        if response.code != 200:
            if response.code == 429:
                logger.error('got HTTP 429 Too Many Requests ; going to sleep a bit...')
                time.sleep(5)
            raise FetchException('fetch error : %s (%s)'%(response.code,response.body))
        data = json.loads(response.body)
        results = data['results']
        results.sort(key=itemgetter('id'))
        logger.info('got %d tweets (last tweet id: %s)',
                    len(results),
                    len(results) and results[-1]['id'] or None)
        for result in results:
            tweet = Tweet.parse(result)
            self.store.append(query, tweet)
        if recurse and data.has_key('next_page'):
            new_url = self.url_base+data['next_page']
            self.handle_response(query, new_url, response)

    @defer.inlineCallbacks
    def _fetch(self, query, url, recurse=True):
        logger.info('fetching: %s',url)
        try:
            response = yield cyclone_fetch(url, headers=self.headers)
            self.handle_response(query, url, response, recurse=recurse)
        except Exception as e:
            logger.error('url fetch error: %s:%s',
                         type(e),
                         e,
                         exc_info=True)

    @defer.inlineCallbacks
    def fetch(self, query):
        last_tweet_id = self.store.retrieve_last_tweet_id(query)
        logger.info('query: %s last query tweet: %s',
                    query, 
                    last_tweet_id)
        url = None
        if not last_tweet_id:
            url = self.first_query_url%{'query':urllib.quote(query)}
            yield self._fetch(query, url, recurse=False)
        else:
            url = self.update_query_url%{'query':urllib.quote(query),'last_tweet_id':last_tweet_id}
            yield self._fetch(query, url)

    def __call__(self):
        logger.info('-- monitor awakened --')
        for query in self.queries:
            self.fetch(query)
