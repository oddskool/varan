varan : realtime twitter monitoring
==========

Purpose
-------

varan is a python server performing real time monitoring of twitter entities.

Features
--------
* realtime monitoring of a configured number of twitter entities (e.g. hashtags)
* configurable "realtime" meaning (up to the second for indexing, think 1-2 digit milliseconds for querying)
* python library & server
* very fast storage based on [redis](http://redis.io)
* very fast web service based on [cyclone](http://cyclone.io)

Demo
----

```shell
PYTHONPATH=. python -m varan.server -c conf/ratp.conf
```

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

