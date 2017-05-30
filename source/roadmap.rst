Project Roadmap
===============

Infrastructure
--------------

* Make it possible to revise data (while keeping all versions).
* Run Jupyterhub, authenticated access to analysis tools and data.
* Run "tmpnb", non-authenticated access to analysis tools and test data for
  teaching an demos.
* Streamline build process using conda forge to decrease time spent releasing
  and distributing updates.
* Create root-prividged conda environments in addition to user-customizable
  conda environments at the beamlines, to ensure all users have read access to
  an "official" release.
* Track performance benchmarks for data retrieval using "air speed velocity"
  utility developed at Space Telescope.

Performance
-----------

* The structure of data storage is optimized to fast insertion and granular
  (e.g., live) retrieval, not bulk retrieval. Add a caching layer optimized for
  bulk retrieval. This cache could be updated by bluesky on runstop, by a cron
  job, or upon first retrieval.

Scalability
-----------

* Back up the databases.
* Add the capability of moving data to an external facility.

Community-Building
------------------

* Mirror other facilities' projects in a single GitHub organization, aimed at
  increasing projects' visibility, aiding discovery, and reducing duplicated
  effort.
* Accumulate a collection of demos and examples covering basic scientific
  stack, as well as tools developed at BNL and other labs.
