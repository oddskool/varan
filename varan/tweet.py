'''
Created on 27 dec. 2012

@author: ediemert
'''
import time
import json
import datetime

class Tweet(object):
    def __init__(self, id_, text, user_id, timestamp, hashtags, geo):
        self.id = str(int(id_))
        self.text = text
        self.user_id = user_id
        self.timestamp = int(timestamp)
        self.hashtags = hashtags
        self.geo = geo
    def __str__(self):
        return u'<Tweet: id="%s" time="%s"/>'%(self.id,
                                               datetime.datetime.fromtimestamp(self.timestamp))
    def __repr__(self):
        return u'<Tweet: id="%s" time="%s"/>'%(self.id,
                                               self.timestamp)
    @classmethod
    def parse(cls, data):
        return Tweet(data['id_str'], 
                     data['text'], 
                     data['from_user'], 
                     int(time.mktime(time.strptime(data['created_at'], 
                                                   '%a, %d %b %Y %H:%M:%S +0000'))),
                     [ h['text'] for h in data['entities']['hashtags'] ], 
                     data['geo'])
    @classmethod
    def deserialize(cls, data):
        data = json.loads(data)
        return Tweet(data['id'],
                     data['text'],
                     data['user_id'],
                     data['timestamp'],
                     data['hashtags'],
                     data['geo'])
    def todict(self):
        return {'id':self.id,
                'text':self.text,
                'user_id':self.user_id,
                'timestamp':self.timestamp,
                'hashtags':self.hashtags,
                'geo':self.geo}
    def serialize(self):
        return json.dumps(self.todict())
