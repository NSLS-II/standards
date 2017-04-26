===============
Suitcase Update
===============

Summary
=======
Suitcase is a simple utility for exporting data from the databroker into a stand-alone, portable file, such as h5 file.


Current Implementation
======================
One of the functions currently used is called "export", which mainly takes header, filename and metadatastore as input and
output h5 file with the same structure of the data in databroker.

Usage Example
-------------

.. code-block:: python

    from suitcase import hdf5
    last_run = db[-1]      # get header from databroker
    hdf5.export(last_run, 'myfile.h5', mds=db.mds)

The first argument may be a single Header or a list of Headers. You can also use keyword "fields"
in the "export" function to define specifically which data sets you want to output.

.. code-block:: python

    from suitcase import hdf5
    hdr = db[123]
    un_wanted_fields = ['A', 'B', 'C']
    fds = hdf5.filter_fields(hdr, un_wanted_fields)
    filename = 'scanID_123.h5'
    hdf5.export(hdr, filename, mds=db.mds, fields=fds)

Here I assume A, B, C are keywords for some vector data, like images. You can define them as un_wanted_fields.
If all vector data are blocked, saving data with only scaler data and header information should be very faster.
Please also define filename clearly, so you know which data it comes from.
