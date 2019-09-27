.. _bl_installation:

Installation at a Beamline
==========================

New Beamline
------------

Install Services
++++++++++++++++

These are instructions are one-time setup for a new beamline. If you are
configuring a new machine at a beamline that already has the software installed
one at least one machine, skip to the next section.

1. On some dedicated server (the standard choice is ``*-ca1``) apply the puppet
   class that installs mongo 3.x some dedicated server and start the mongo
   daemon.

Create Conda Environments
+++++++++++++++++++++++++

.. note::

   DAMA deploys the conda environments using Ansible. See
   :doc:`deployment_docs` for more details.

Install Scripts
+++++++++++++++

Two convenience scripts, ``fix_conda_privileges.sh`` should be installed in
``/usr/local/bin``. ``bsui`` installation is a part of the Ansible workflow.

* ``fix_conda_privileges.sh`` works around a bug in conda wherein users cannot
  properly access root-installed conda packages. It should be run after
  creating or updating and conda environments in ``/opt/conda_envs``, as shown
  above.
* ``bsui`` is a shortcut script that activates a conda environment and starts
  IPython with the 'collection' profile.

Create New IPython Profile
++++++++++++++++++++++++++

At NSLS-II we use IPython profiles to run startup scripts for user convenience.

Profiles are stored in (or soft-linked) from ``~/.ipython`` in the user profile
of individual users or shared beamline accounts.

The standard profile is called "collection," and the startup scripts are
located in ``~/.ipython/profile_collection/startup/``.

If this beamline does not yet have an IPython profile for data collection under
version control, create one. Start IPython with this command, and then exit.

    .. code-block:: bash

        ipython --profile=collection

    .. note::

        The official IPython documentation has more information on
        `IPython profiles <https://ipython.org/ipython-doc/dev/config/intro.html#profiles>`_

The above command created new directores and some files under
``~/.ipython/profile_collection``. We add startup files by writing Python
scripts in the subdirectory ``startup/`` in this profile directory.


Create a Beamline GitHub Organization
+++++++++++++++++++++++++++++++++++++

1. Create a username on `github.com <https://github.com>`_ if you don't have
   one. Create a new organization with the name ``NSLS-II-XXX`` where ``XXX``
   is the three-letter (sometimes four and more) beamline abbreviation (e.g.,
   ``ISS``). Create a new repository in this organization named
   ``profile_collection``.

2. Make the new IPython profile a git repository.

.. code-block:: bash

    cd ~/.ipython/profile_collection
    git init
    git add startup/
    git commmit -m "initial commit"


3. Upload the ``profile_collection`` git repository to GitHub. Be sure to edit
   the command below to replace ``NSLS-II-XXX`` with the name of your
   organization.

.. code-block:: bash

    git remote add upstream https://github.com/NSLS-II-XXX/profile_collection.git
    git push -u upstream master


Configure the Olog
++++++++++++++++++

Essential Configuration
^^^^^^^^^^^^^^^^^^^^^^^

``pyOlog`` requires a configuration file to specify the connection settings. As
root, create a file at ``/etc/pyOlog.conf`` with the following contents::

    [DEFAULT]
    url = https://<beamline>-log.cs.nsls2.local:8181/Olog
    logbooks = Commissioning   # use the name of an existing logbook
    username = <username>
    password = <password>

where ``<beamline>`` is the designation formatted like ``xf23id1``.

Integration with Bluesky
^^^^^^^^^^^^^^^^^^^^^^^^

Bluesky automatically logs basic scan information at the start of a
scan. (All of this information is strictly a subset of what is
also stored in metadatastore -- this is just a convenience.)

Back in an IPython profile startup file, add::

    from functools import partial
    from pyOlog import SimpleOlogClient
    from bluesky.callbacks.olog import logbook_cb_factory

    # Set up the logbook. This configures bluesky's summaries of
    # data acquisition (scan type, ID, etc.).

    LOGBOOKS = ['Data Acquisition']  # list of logbook names to publish to
    simple_olog_client = SimpleOlogClient()
    generic_logbook_func = simple_olog_client.log
    configured_logbook_func = partial(generic_logbook_func, logbooks=LOGBOOKS)

    cb = logbook_cb_factory(configured_logbook_func)
    RE.subscribe('start', cb)

Integration with Ophyd
^^^^^^^^^^^^^^^^^^^^^^

Ophyd has as ``log_pos`` method that writes the current position of all
positioners into the log. To enable this, add the following to an IPython
profile startup file, add::

    # This is for ophyd.commands.get_logbook, which simply looks for
    # a variable called 'logbook' in the global IPython namespace.
    logbook = simple_olog_client

The log entires will be written into the logbook specified in
``.pyOlog.conf`` (in our example, "Commissioning"), not the logbook
used by bluesky (in our example, "Data Acquisition").

Olog IPython "Magics"
^^^^^^^^^^^^^^^^^^^^^

"Magics" are special IPython commands (not part of Python itself). They
begin with %. There are two IPython magics for conveniently writing to
the Olog.

* Type ``%logit`` to quickly type a text log entry.
* Type ``%grabit``, select an area of the screen to capture, and type in a
  text caption.

These require their own special configuration. In the profile directory, such
as ``~/.ipython/profile_collection``, edit the file ``ipython_config.py``.

Add the line::

    c.InteractiveShellApp.extensions = ['pyOlog.cli.ipy']

The log entires will be written into the logbook specified in
``.pyOlog.conf`` (in our example, "Commissioning"), not the logbook
used by bluesky (in our example, "Data Acquisition").

New User
--------

One-time configuration
++++++++++++++++++++++

Add the following to the user's ``~/.bashrc`` file.

.. code-block:: bash

    source /etc/profile.d/proxy.sh
    source /opt/conda/etc/profile.d/conda.sh

The first line adds local NSLS-II controls network configuration. It should
already be set at the system level but in practice they are often not.

Conda has already been installed (or will be installed as a part of an Ansible
push) on all NSLS-II workstations (ws) and servers (srv) in a shared location.
The second line adds a ``conda`` command to the user's environment.

Convenience Script ``bsui``
+++++++++++++++++++++++++++

The script ``bsui``

Creating or Updating Shared (Root) Environments
+++++++++++++++++++++++++++++++++++++++++++++++

Administrators with sudo access can create or update conda environments that
users can use ("activate") but only administrators can edit. These environments
are located in ``/opt/conda_envs``.

.. note::

    To review the detailed conda configuration, refer to
    ``/opt/conda/.condarc``, where you can see the list of default channels and
    the search path for environments.


Installing on a Personal Computer
---------------------------------

You can install these packages on your personal laptop outside the controls
network. Install miniconda or Anaconda, and create user environments as
described below. All of the packages are mirrored on anaconda.org, outside of
the NSLS-II firewall, where you will be able to access them. The channel is
called ``lightsource2-tag`` instead of ``nsls2-tag``. The following serves as a
step by step guide:

#.  Follow the instructions in the link below to install minconda or anaconda.

        https://conda.io/projects/conda/en/latest/user-guide/install/index.html

#.  Open a terminal and run the following commands to install the enviroments. 

    .. code-block:: bash

        conda create -n collection-2019-3.0 -c lightsource2-tag collection=2019C3.0
        conda create -n analysis-2019-3.0 -c lightsource2-tag analysis=2019C3.0

    .. note::

       The ``collection-2019-3.0`` or ``analysis-2019-3.0`` part of these
       commands relates to the released versions from the third cycle of 2019;
       you can use any version here.

    .. warning::

       There is a conda channel named ``lightsource2`` that it no longer
       maintained. If you use it, you will find very old versions of some of
       the packages used at NSLS-II. Use ``lightsource2-tag`` instead.

#.  Check this worked by running the command below:
    .. code-block:: bash

        conda env list

    You should see ``collection-2019-3.0`` listed (or whichever version you
    installed).
