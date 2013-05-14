varan : realtime twitter monitoring
==========

Purpose
-------

varan is a python server performing real time monitoring of twitter entities.

Features
--------
* realtime monitoring of twitter entities (e.g. hashtags)
* configurable "realtime" meaning (up to the second for indexing, think 1-2 digit milliseconds for querying)
* python library & server
* very fast storage based on [redis](http://redis.io)
* very fast web service based on [cyclone](http://cyclone.io)

Dependencies
------------
* python 2.7+
* redis 2.2+
* [tweetstream](https://bitbucket.org/runeh/tweetstream/src)

On Ubuntu 12.x it is recommended to setup your box like this:

```shell
sudo apt-get install redis-server
sudo `which pip` install -r requirements.txt
hg clone https://bitbucket.org/runeh/tweetstream && cd tweetstream && python setup.py bdist_egg
```

In case you don't have `pip` installed, you can:
```shell
wget http://pypi.python.org/packages/2.7/s/setuptools/setuptools-0.6c11-py2.7.egg
sudo bash setuptools-0.6c11-py2.7.egg
sudo `which easy_install` pip
```

Demo
----

Launch the server:
```shell
PYTHONPATH=../tweetstream/dist/*egg:. python -m varan.server -c conf/ratp.conf
```
Then point your brower to `http://localhost:8989/web/index.html`

Alternatively, you can see a nice monitoring of Paris urban transport [here](http://varan.komodo.re/web/index.html) (best viewed with Firefox)

Stability
---------

varan is still a prototype. see [TODO](https://github.com/oddskool/varan/blob/master/TODO.md). 

hand-tested on python 2.7.x, redis 2.2+, cyclone 1.0+

License
-------

MIT. see [LICENSE](https://github.com/oddskool/varan/blob/master/LICENSE)

Name
----

varan is another name for [monitor lizard](https://en.wikipedia.org/wiki/Monitor_lizard)

