*******************************
Format of Metadatastore Entries
*******************************

Introduction
============

The metadatastore is based on the concept of documents which are either
events, or descriptions of events.  An ``event`` is a quantum of data
stored in the metadata store and represents an *action* at a given time. For
example: "*measurement of 8 scaler chanels*", "*trigger detectors*" or
"*start run*".

Expanding the notion of **events**, these can also be used for derived data.
For example, an event could be the result of a data analysis or reduction
routine which was run at a certain time.

The document schemas in this document are written using ``jsonschema``.  The
full spec http://json-schema.org/ is basically un-readable.  A more readable
introduction https://spacetelescope.github.io/understanding-json-schema/index.html.


.. todo::
    Expand this section




Time
====

One of the cornerstones of this data acquisition and analysis method is the use
of *time* as the method by which data can be aligned and correlated. A single
``event`` should have happened at a certain quantum of time with the
determination of what a time *quantum* is left to the details of the
experiment. Time however, can be horrendously messy. Throughout this
section we use two terms, ``timestamp`` and ``time``. These mean


time
    The date/time as found by the client when an ``event`` is
    created.  This could be a date-time format as determined by the underlying
    storage method (for example a database).

timestamp
   A (usually *float*) representation of the hardware time when a
   certain value was obtained. Wherever possible this should be read from
   hardware. For example, this could be the *EPICS* timestamp from when the
   record processed which provides the value.


We use the literal ``<time>`` to indicate a client side date/time and
``<timestamp>`` to represent the numerical timestamp.

.. todo::
    Add dictionary of reserved keys such as ``timestamp``, ``id``
    Expand for data collection, using event model


Events view of the world
========================

.. highlight:: json

When taking data we measure numbers ::

  2.5

Well, typically more than one number ::

  [2.5, .05]

but then we need to know *what* we measured ::

   {
    "motor1": 2.5,
    "photodiode":0.05
   }

and we tend to want to measure the same things many times in
sequence so we should keep track of the sequence number ::

  {
   "seq_num": 0,
   "data": {"motor1": 2.5,
            "photodiode":0.05}
  }
  {
   "seq_num": 1,
   "data": {"motor1": 2.4,
            "photodiode":0.5}
  }

and we also want to know *when* we took the data and be able to uniquely identify
a given event ::

  {
   "seq_num": 0,
   "data": {"motor1": 2.5,
           "photodiode":0.05},
   "time": 1431698798.9090064,
   "uid": "82d81f96-2c81-42a4-90e7-9f1c96e5709b"
  }
  {
   "seq_num": 1,
   "data": {"motor1": 2.4,
            "photodiode":0.5},
   "time": 1431698800.8632064
   "uid": "9912c195-aa5d-4404-b529-823f2a2e30a2"
  }

However, the data we are measuring is coming from real pieces of hardware which never get
measured at *exactly* the same time so we also want to store those times ::


  {
   "seq_num": 0,
    "data": {"motor1": [2.5, 1431698798.9090054],
            "photodiode": [0.05, 1431698798.9090060]},
    "time": 1431698798.9090064,
    "uid": "82d81f96-2c81-42a4-90e7-9f1c96e5709b"
  }
  {
   "seq_num": 1,
   "data": {"motor1": [2.4, 1431698800.8632061],
            "photodiode": [0.5, 1431698800.8632062]},
   "time": 1431698800.8632064
   "uid": "9912c195-aa5d-4404-b529-823f2a2e30a2"
  }

For non-scalar data we do not want to store the raw data directly in the events.
This is both for technical reasons on both the data base side and the collection side
non-scalar data is stored external to the events and only a reference is stored in
the documents ::

  {
   "seq_num": 0,
    "data": {"cam1": ["c0a687b9-2413-4e18-9bc6-97fe5f049814", 1431698798.9090053],
             "motor1": [2.5, 1431698798.9090054],
             "photodiode": [0.05, 1431698798.9090060]},
    "time": 1431698798.9090064,
    "uid": "82d81f96-2c81-42a4-90e7-9f1c96e5709b"
  }
  {
   "seq_num": 1,
   "data": {"cam1": ["4e65245a-88a2-490f-9916-a48c4cf57d68", 1431698800.8632051],
            "motor1": [2.4, 1431698800.8632061],
            "photodiode": [ 0.5, 1431698800.8632062]},
   "time": 1431698800.8632064
   "uid": "9912c195-aa5d-4404-b529-823f2a2e30a2"
  }


We call these documents "Events" and they capture almost all of the
scientific information about a measurement.  By bundling all of these
measurements into a single document the experimenter is communicating that
this set of measurements are "naturally" associated with each other and are,
to the experimental time scale that matter, "at the same time".  A stream
of Events represents a single completely synchronous experiment.

However, Events alone do not tell us:

- where is the external data stored and how do we get it?
- what hardware was used to take each data

and in general we have no way of knowing ahead of time:

- what the keys in "data" will be
- what the data type will be
- if the value is real data or a reference
- the data shape

For a single data entry the source of the data can be uniquely
specified with a PV ::

 {
  "source": "PV:XF23ID{}-RBV"
 }

the dtype and shape are book keeping::


 {
  "source": "PV:XF23ID{}-RBV",
  "dtype": "number",
  "shape": []
 }

and if the data is stored externally then a an "external" key
holds::


 {
  "source": "PV:XF23ID{}:CAM-ARR",
  "dtype": "array",
  "shape": [2000, 2000],
  "external": "FILESTORE"
 }

To fully describe the events we thus assemble a EventDescriptor::

  {
   "uid": "3fa1f82b-c106-48dd-b612-c038a487348c",
   "time": 1431708954.9472792,
   "data_keys": {"cam1": {
                          "source": "PV:XF23ID{}:CAM-ARR",
                          "dtype": "array",
                          "shape": [2000, 2000],
                          "external": "FILESTORE"
			 },
		"motor1": {
		           "source": "PV:XF23ID{}:motor-RBV",
			   "dtype": "number",
			   "shape": []
			  },
		"photodiode": {
		           "source": "PV:XF23ID{}:pd-I",
			   "dtype": "number",
			   "shape": []
			  }
		  }
  }

and the go back and add a reference to the EventDescriptor to our Event
documents::

  {
   "seq_num": 1,
   "data": {"cam1": ["4e65245a-88a2-490f-9916-a48c4cf57d68", 1431698800.8632051],
            "motor1": [2.4, 1431698800.8632061],
            "photodiode": [ 0.5, 1431698800.8632062]},
   "time": 1431698800.8632064
   "uid": "9912c195-aa5d-4404-b529-823f2a2e30a2",
   "descriptor": "3fa1f82b-c106-48dd-b612-c038a487348c",
  }

which allows us to: given an Event look up what is in it and given an
EventDescriptor get all of the Events which are described by it.

However, event with EventDescriptors we are still not capturing
everything about the experiment which might be relevant.  For example
we have described the 'what' of the measurement, but not the
'who', 'how', 'why', or 'where'.  For that we need another layer of documents which capture things
like

- what research project this is part of?
- what beamline the data is taken at?
- what sample is in the beam?
- how is the beam line configured?
- who owns this data?

Thus we also have a RunStart Document that looks like::

 {
  "uid": "c8333990-fc9b-4dd0-b1b1-41efc47a4ef5",
  "time": 1431710613.1099296,
  "project": "review docs",
  "beamline_id": "backyard",
  "scan_id": 0,
  "beamline_config": {"ant_hills": 2, "ant_type": "small"},
  "owner": "tcaswell",
  "group": "DAMA",
  "sample": {"name": "aardvark", "color": "brown"}
}

and then add a reference to the RunStart uid in the EventDescriptor documents ::


  {
   "run_start": "c8333990-fc9b-4dd0-b1b1-41efc47a4ef5",
   "uid": "3fa1f82b-c106-48dd-b612-c038a487348c",
   "time": 1431708954.9472792,
   "data_keys": {"cam1": {
                          "source": "PV:XF23ID{}:CAM-ARR",
                          "dtype": "array",
                          "shape": [2000, 2000],
                          "external": "FILESTORE"
                         },
                "motor1": {
                           "source": "PV:XF23ID{}:motor-RBV",
                           "dtype": "number",
                           "shape": []
                          },
                "photodiode": {
                           "source": "PV:XF23ID{}:pd-I",
                           "dtype": "number",
                           "shape": []
                          }
                  }
  }

There can be a many-to-one relationship between EventDescriptors and
RunStarts.  This is useful when a given 'run' may have more that one
asynchronous event stream.  For example measuring a scalar values
(tempreature, voltage, etc) at 5 Hz while taking 10s exposures with an
area detector.  By de-coupling measurements that can be asynchronous
each measurement can be made at the 'right' speed.

To go with the RunStart document there is a RunStop document which reports
the final fate of the run::

 {
   "time": 1431714441.0788312,
   "run_start": "c8333990-fc9b-4dd0-b1b1-41efc47a4ef5",
   "exit_status": "success",
   "reason": "",
   "uid": "18001952-638d-4c02-835c-eda8e5dc2e92"
 }




Documents
=========

.. xfig:: mds.fig




Event Descriptor Document
=========================


Schema
++++++

.. schema_diff::

    // Proposed
    ev_desc_prop.json
    --
    // as documented
    ev_desc_doc.json
    --

    // As currently (1c2246d) implemented
    ev_desc_impl.json


Definitions
+++++++++++

data_key
~~~~~~~~
{"source": "NAMESPACE:NAME", "external": "NAMESPACE:NAME"}

source
  The reference to the physical piece of hardware that produced this data

external, optional
  The reference to the location where the data is being stored.
  If this key is not present, then the data is stored inside the data
  field of the corresponding ``Event`` document.
  If this key is present, then the ``value`` field of the ``data``
  dictionary inside the ``Event`` document is interpreted as a unique
  key that can be used to retrieve corresponding data from the
  service described by the value of the ``external`` key

The values of both =source= and =external= are (=namespace=, =name=) pairs.
The name is obligatory for source and optional for external

NAMESPACE
   Things like ``PV`` or ``FileStore``.
NAME
   Thing in the name space.



Example
+++++++

Event descriptors are used to describe an array of events which can form an
event stream of a collection of events. For example a run forms
event_descriptors at run start to define the data collected. For the example
above ``event`` is described by the ``event_descriptor``

.. ipython:: python

  import json
  import jsonschema
  ev_desc = {
      "uid": "f05338e0-ed07-4e15-8d7b-06a60dcebaff",
      "keys": {
          "chan1": {"source": "PV:XF:23ID1-ES{Sclr:1}.S1", "dtype": "number", "shape": None},
          "chan2": {"source": "PV:XF:23ID1-ES{Sclr:1}.S2", "dtype": "number", "shape": None},
          "chan3": {"source": "PV:XF:23ID1-ES{Sclr:1}.S3", "dtype": "number", "shape": None},
          "chan4": {"source": "PV:XF:23ID1-ES{Sclr:1}.S4", "dtype": "number", "shape": None},
          "chan5": {"source": "PV:XF:23ID1-ES{Sclr:1}.S5", "dtype": "number", "shape": None},
          "chan6": {"source": "PV:XF:23ID1-ES{Sclr:1}.S6", "dtype": "number", "shape": None},
          "chan7": {"source": "PV:XF:23ID1-ES{Sclr:1}.S7", "dtype": "number", "shape": None},
          "chan8": {"source": "PV:XF:23ID1-ES{Sclr:1}.S8", "dtype": "number", "shape": None},
          "pimte": {"source": "CCD:name_of_detector", "external": "FILESTORE",
                    "dtype": "array", "shape": [1254, 2014]}
      },
      "begin_run_event": "2dc386b5-cfee-4906-98e9-1a8322581a92",
      "time": 1422940263.7583334,
  }
  with open('source/arch/ev_desc_prop.json') as fin:
      schema_prop = json.load(fin)

  jsonschema.validate(ev_desc, schema_prop) is None

Note that ``validate`` returns ``None`` for documents that pass and raises
exceptions for those that do not.

Discussion points
+++++++++++++++++

- Should ``begin_run_event`` be a mandatory?


Event Documents
===============

Schema
++++++
.. schema_diff::
  // As documented
  event.json
  --

  // As implemented

  {
      "definitions": {
          "data": {
              "properties": {
                  "timestamp": {
                      "type": "number"
                  },
                  "value": {
                      "type": [
                          "string",
                          "number"
                      ]
                  }
              },
              "required": [
                  "value",
                  "timestamp"
              ],
              "type": "object"
          }
      },
      "properties": {
          "data": {
              "additionalProperties": {
                  "$ref": "#/definitions/data"
              },
              "type": "object"
          },
          "descriptor": {
              "type": "string"
          },
          "seq_no": {
              "type": "number"
          },
          "time": {
              "type": "number"
          },
          "time_as_datetime": {
              "type": "string"
          }
      },
      "required": [
          "data",
          "time",
          "descriptor",
	  "seq_no"
      ],
      "type": "object"
  }


The field ``seq_num`` is used to order the events in the order in which they were
created.

Example
+++++++

Measure events contain the data measured at a certain instance in time or
explicit point in a sequence. For example::

    {
        "uid": "4609e51f-cf38-4c2a-a6ea-483edc461e43",
        "seq_num": 42,
        "descriptor": "f05338e0-ed07-4e15-8d7b-06a60dcebaff",
        "data": {
            "chan1": [3.14, 1422940467.3101866],
            "chan2": [3.14, 1422940467.3101866],
            "chan3": [3.14, 1422940467.3101866],
            "chan4": [3.14, 1422940467.3101866],
            "chan5": [3.14, 1422940467.3101866],
            "chan6": [3.14, 1422940467.3101866],
            "chan7": [3.14, 1422940467.3101866],
            "chan8": [3.14, 1422940467.3101866],
            "pimte": ["8cad7f02-c3e1-4e76-a823-94a2a7d23f6b",
                      "timestamp": 1422940481.8930786]
        },
        "time": 1422940508.3491018,
    }

Where the keys ``uid``, ``ev_desc``, ``time`` and ``timestamp`` refer to
the unique id, a link to the event descriptor the time and the EPICS timestamp
respectively.


Start Run Events
================


Schema
++++++
.. schema_diff::

  // As documented
  begin_run_event.json
  --

  // As implemented

  {
        "properties": {
          "beamline_config": {
              "type": "object"
          },
          "beamline_id": {
              "type": "string"
          },
          "custom": {
              "type": "object"
          },
          "owner": {
              "type": "string"
          },
          "scan_id": {
              "type": "string"
          },
          "time": {
              "type": "number"
          },
          "time_as_datetime": {
              "type": "string"
          }
      },
      "required": [
         "time",
         "owner",
         "beamline_id"
      ],
      "type": "object"
  }


Example
+++++++

The beginning of a data collection run creates an event which contains
sufficient metadata and information to describe the data collection. For
example, this is where beamline config information is located. The start run
event also serves as a searchable entity which links all data associated by an
event. For example::

    {
        "uid": "2dc386b5-cfee-4906-98e9-1a8322581a92",
        "scan_id": "ascan_52",
        "beamline_id": "CSX",
        "sample": {
            "uid": "0a785292-05c5-4c1b-bd9a-f2dd5b0580c8",
            "id": 9,
            "description": "A small piece of cheese"
        },
        "project": "Cheese_shop",
        "beamline_config": {
            "diffractometer": {
                "geometry": "swiss",
                "xtal_lattice": {
                    "a": 1.1,
                    "b": 2.2,
                    "c": 3.3,
                    "alpha": 4.4,
                    "beta": 5.5,
                    "gamma": 6.6
                },
                "UB": [1, 2, 3, 4]
            }
        },
        "time": 1422940625.2198992,
        "owner": "jcleese",
        "group": "monty"


    }



End Run Events
==============

Schema
++++++

.. schema_diff::

  // As Documented
  end_run_event.json
  --
  // As implemented


  {
      "properties": {
          "begin_run_event": {
              "type": "string"
          },
          "custom": {
              "type": "object"
          },
          "reason": {
              "type": "string"
          },
          "time": {
              "type": "number"
          },
          "time_as_datetime": {
              "type": "string"
          }
      },
      "required": [
          "begin_run_event",
          "time"
      ],
      "type": "object"
  }


Example
+++++++


With the corresponding end run event as::

    {
        "uid": "60bac4c7-e2d3-4c4b-a553-3790a8add866",
        "begin_run_event": "2dc386b5-cfee-4906-98e9-1a8322581a92",
        "reason": "This shop does not contain any cheese",
        "completion_state": "fail",
        "time": 1422940679.72617,
    }

The field ``reason`` can be used to describe why a run ended e.g. was it aborted or
was there an exception during data collection. The field ``begin_run_event`` is a
pointer to the start document.
