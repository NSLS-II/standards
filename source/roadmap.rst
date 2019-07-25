***************
Project Roadmap
***************

Review of Current Status
------------------------

The "bluesky software suite" includes components for experiment specification
(bluesky), device abstractions (ophyd), and data storage and access (data
broker).

Deployment at NSLS-II
=====================

Bluesky is deployed at all operational NSLS-II beamlines and regularly used at
all but a couple of them.

Notably, beamline scientists are writing sophisticated plans (bluesky jargon
for experiment procedures) on their own, and some have even made direct code
contributions to the bluesky library, validating our hypothesis that
participation from scientists will help the project scale. This has been
supported by hundreds of hours of tutorials and comprehensive documentation.

External Collaborations
=======================

The project has been presented at ORNL, APS, SLAC, and the Australian
Lightsource, and installed for testing on beamlines at APS, SLAC, and ORNL.

Current Feature Set
===================

* Step scans (N-dimensional, complex spiral trajectories, anything we can think
  of)
* Fly scans
* Reciprocal space scans
* Adaptive plans (e.g. feed measurements back into plan)
* Composable plans (e.g. they can be chained together)
* Sophisticated streaming analysis (e.g. live tomographic reconstruction)
* Manual and automatic suspend/resume (e.g. in response to beam dump)
* Simulation mode
* Search on arbitrary metadata (user groups can use whatever systems make sense
  to them)
* Automated end-of-run data export to TIFF, CSV, HDF5, etc.
* Sample management inventory database
* Integration with Olog
* Demonstrated integration with PyXRF, a fluorescence fitting GUI
* Integration with beamline-specific code built upon bluesky (e.g. ‘xpdacq’)
* Guaranteed "cleanup" protocols that make hardware safe in the event of an
  interruption
* Support for all known EPICS-compatible hardware on the floor
* Transport of streaming data over the network via 0MQ
* A basic GUI for browsing saved data
* A publicly available sandbox deployment is available at try.nsls2.bnl.gov
  for training and testing purposes.

Known Outstanding Needs from a Beamline Perspective
===================================================

* Need GUIs for acquisition and analysis customized to beamline needs.
* Need better data browsing, both at the beamline and remotely.
* Need access control on user data. (At NSLS-II, progress is currently blocked
  by issues outside of the project's scope.)
* Needs better log book functionality and integration.
* Make plans more modular to make multi-run plans easier.

1.0 Release Planned for End of 2017
-----------------------------------

Potentially Disruptive Changes
==============================

Several ideas or known issues may require making changes to the API that would
break user code, so they should be done before the release of 1.0 if possible.
These are:

* Reorganize the data broker codebase to support a variety of underlying
  storage technologies. This will better support high-throughput beamlines
  (e.g., HXN, SRX, LIX) and accommodate potential collaborators (e.g., ALS).
* Review "rewinding" behavior (related to pause/resume support).
* Investigate possibility of executing multiple bluesky "plans" at once.
* Perform a major code refactor that separates the bluesky RunEngine's I/O
  bundling code from its interruption handling code.
* Integrate caproto, and support an asynchronous interface between bluesky and
  ophyd.
* Allow updates (revisions) to saved data.
* Develop minimal facility-wide standards for metadata names. These will not
  necessarily be enforced on beamlines that don't need them but they will at
  least serve as defaults.
* Rethink modularity of plans to make it easier to do multi-run experiments.
* Revisit early "SPEC-like" plans to simplify and unify the interface.
* Provide better best-effort visualization and processing, incorporating ideas
  from VegaLite and also Nexus's "default plot".

Non-distruptive Changes
=======================

* Identify common device configuration across beamlines and move it into a shared
  repository. (Of course, this has already been to some extent but it's an
  ongoing process.)
* Provide more tools for visualizing and simulating plans.
* Provide basic feature for commenting on or tagging datasets.
* Better tooling around Area Detector.
* Allow cameras to be used in writing or non-writing modes from ophyd more
  conveniently.
* Utilize new Python features to simplify ophyd's codebase.

Two-Year Plan
-------------

* Deploy experimental GUI for composing and executing plans.
* Deploy minimal "analysis store," a data broker-like interface to analyzed
  data.
* Explore better provenance handling in "analysis store."
* Integrate with the PASS system.
* Protect all data access by putting it behind a network service with access
  control.
* Choose a data format for long-term archival.
* Integrate with cloud services like Globus, Dropbox, Google Cloud, and Amazon
  Web Services.
* Support more export formats (e.g. Nexus).
