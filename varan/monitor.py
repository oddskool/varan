'''
Created on 27 dec. 2012

@author: ediemert
'''
from cyclone.httpclient import fetch as cyclone_fetch

from varan import VERSION, logger

class Monitor(object):

    def __init__(self, queries, store):
        self.url_base = 'https://search.twitter.com/search.json'
        self.first_query_url = '%s?q=%%(query)s&result_type=mixed&count=1' % self.url_base
        self.update_query_url = '%s?q=%%(query)s&result_type=mixed&since_id=%%(last_tweet_id)s' % self.url_base
        self.headers = { 'Connection':'close',
                         'Accept':'application/json',
                         'User-Agent':'varan %s - https://github.com/oddskool/varan - contact: oddskool+varan@gmail.com'%VERSION }
        self.queries = queries
        self.store = store

    def fetch(self, query):
        logger.info('query: %s',query)
        last_tweet_id = self.store.retrieve_last_tweet_id(query)
        url = last_tweet_id and self.update_query_url%{'query':query,'last_tweet_id':last_tweet_id} or self.first_query_url%{'query':query} 
        logger.info('fetching: %s',url)
        try:
            return cyclone_fetch(url, headers=self.headers)
        except Exception as e:
            logger.error('url fetch error: %s:%s',
                         type(e),
                         e,
                         exc_info=True)

    def __call__(self):
        for query in self.queries:
            data = self.fetch(query)
            logger.info(data)
