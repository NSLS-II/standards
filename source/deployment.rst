.. highlight:: bash

Deployment
==========

Building a Tagged Version
--------------------------

Tagging
=======

Generally, we increment the micro version and create a new tag.::

   git tag x.y.z
   git push NSLS-II --tags

Copy the conda recipe in conda-prescriptions/releases/REPO_NAME/
into a new directory and update the hard-coded version and git tag.


Building
========

   cd DIRECTORY  # e.g., conda-prescriptions/releases/dataportal/v0.0.2
   conda build .


Building an Untagged Commit
----------------------------

It is OK to build and upload an untagged commit. Conda will label
the version with a `.post` designation that tracks the number of
commits since the last tag. Therefore, the ordering will be correct
as long as all of the builds are from master. Uploading builds from
other branches (which have their own commit count) may cause the
ordering to break.

   cd DIRECTORY  # e.g., Repos/dataportal
   git fetch --tags NSLS-II
   conda build .


Deploying to Binstar
--------------------

First, upload the binary tarball built above. You can use
``binstar upload  FILENAME`` or use this trick that gets the filename
from conda:::

   binstar upload `conda build . --output`

Log in to binstar (``binstar login``) and then use the ``copy`` subcommand
below. Included is the stdout as proof that this worked at least one (1) time.

Notice that the designation of "channel" is confusing here. We are copying
from the main channel of IXS, where the build was originally uploaded, to

   binstar copy --from-channel main \
   --to-owner CSX --to-channel main \
   IXS/dataportal/v0.0.4
   Using binstar api site https://conda.nsls2.bnl.gov/api
   Copied file: linux-64/dataportal-v0.0.4-py27_0.tar.bz2
   Copied 1 files

Greedy copying (``IXS/`` or ``IXS/*`` or ``IXS/dataportal/`` etc.) do not seem
to work. Let's make a bash script someday.
