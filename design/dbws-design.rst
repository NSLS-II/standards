=================================
Data Broker Service Layer Design
=================================

Motivation
==========

Databroker has been actively developed and widely used over the past 2 years. 
It has become more powerful and stable thanks to Dan Allan's efforts over the
past year. Its stability and wide acceptance as the de facto way access data
acquired in our beamlines. A new wave of requirements are reported as a result
of our community outreach. One of these requirements is a set of databroker
server implementations that will allow remote access to experimental data over
network. The service layer will also eliminate any issues that may occur as a
result of providing direct/library-level access to databases, allowing 
us to implement data access policies.

Challenges
===========

NSLS-II and other facilities have a wide variety of experimental setups that
generate data at different rates and structure. This poses a major challenge
for a single-backend implementation. Another challenge is the lack of sys admin
and dev-ops support. Making performant and reliable asynchronous servers with 
low-latency is that are maintainable in the long term that are easy to deploy
is especially difficult with the amount of resources at hand.


Roadmap
===========

- Identify the data rates required to be transferred in NSLS-II databases. This
does not require a major effort, a simple investigation of existing metadatastore
and filestore will suffice

- Identify the technologies to be used for transmitting ND arrays over the wire:
  msgpack, protobuffe, h5serv, etc. This includes performance measurements 

- Have a first cut on existing databroker using .. _ujson: http://artem.krylysov.com/blog/2015/09/29/benchmark-python-json-libraries/

- Prioritize the backends to be implemented, define timelines, and implement.

- Add an authentication layer


Technology
=============

Given there are plans for central storage and data management, the implementation
of the server layer must be scalable. This means a micro-service oriented
infrastructure that can eventually be placed behind load balancers is a good
intuitive choice. A fully RESTful approach is achiveable yet limiting given the
flexibility provided by the stack. This layer needs some discussion. We could
definitely adopt a RESTful approach (ugh, dreaded approach word) could be
adopted rather than handler per document type sort of approach of metadataservice
and amostra.

Server Side Design
===================

HeaderHandler
------------

**get:** Decode jsonified query and return a serialize a list of dicts
If invalid request, return appropriate http error code.


EventSourceHandler
------------------

**get:** Using the uid of the descriptor(s), obtains an event generator.
By paginating on this generator, returns the payload to the client side.
In the future, this bit will sort out the source of the data fill source
and redirect to the appropriate handler. In this context, handler refers to
the eventsource provided specific choice of technology given the data structure
and rate.
