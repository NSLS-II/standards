Automating Deployment with Puppet
=================================
Definitions
-----------
* BEAMLINE_WORKSTATION
    Any computer that beamline staff designate as a computer they want the
    collection stack installed on
* BEAMLINE_SERVER
    The main "compute" computer where jupyterhub will point to
* BEAMLINE_USER
    The beamline user name. `xf23id1`, `xf11id`, etc...
* IPYTHON_CONFIGURATION:
    The files that are used to configure the data collection environment.
    These have thus far been a collection of files that are prefixed with
    two numbers and are stored in ~/.ipython/profile_collection or a variant
* IPYTHON_CONFIGURATION_LOCATION:
    Proposed to be at `~/ipython_profile`. Or maybe `~/bluesky_configuration` is better
* IPYTHON_CONFIGURATION_NAME:
    Currently it is `collection` at most places. I think we should standardize
    on this.
* {{ BEAMLINE }}
    Placeholder syntax for any beamline ID, i.e., LIX, CHX, XPD, CSX, etc...
* {{ BEAMLINE }}_CONFIGURATION
    Conda package that includes the configuration information for at least
    metadatastore and filestore.  Optionally includes configuration information
    for a local channelarchiver server.  Other configuration information is
    welcome to be put in here.  BACKUP_LOCATION is something that should be
    added into the this configuration package
* COLLECTION
    Conda metapackage that enumerates the conda packages that make up our
    collection environment
* COLLECTION_{{ BEAMLINE }}
    Conda metapackages that are beamline specific and include any extra
    packages that a beamline needs or wants installed in their collection
    environment.
* ANALYSIS
    conda metapackage that enumerates the conda packages that make up our
    analysis environment
* ANALYSIS_{{ BEAMLINE }}
    conda metapackage that is beamline specific and includes at least the
    analysis metapackage and the {{ BEAMLINE }}_configuration conda package
* OLOG
    Logbook for everything {{ BEAMLINE }} related
* UAT
    User acceptance tests. These are the tests that, when successfully run,
    allows us to declare victory that our software stack is still working as
    intended on each beamline.  Note that these UAT's are the beamline's
    responsibility to create and maintain as it is just simply not possible
    for the DAMA group to know every way that each beamline is using the
    software stack.

Automated installation procedure for collection environment
-----------------------------------------------------------
0. Define some bash functions to make notifications easier... ::

    notify_slack ()
    {
        curl -d "title=$1&body=$2&room=$3" http://penelope:5000/message
    }

    log_to_olog ()
    {
        # log the files that were changed to the logbook.
        su - {{ BEAMLINE_USER }}
        source activate collection
        python -c "from pyOlog.cli.ipy import olog; import os; olog(msg=$1, logbooks='DAMA Software')"

    }
1. Commit all python files that are in {{ IPYTHON_CONFIGURATION_LOCATION }}/profile_{{ IPYTHON_CONFIGURATION_NAME }} ::

    su - {{ BEAMLINE_USER }}
    pushd $HOME/{{ IPYTHON_CONFIGURATION_LOCATION }}/profile_{{ IPYTHON_CONFIGURATION_NAME }}
    find -name *.py -exec git add {} \;
    git commit -am "Automated weekly code backup: `date +%Y-%W`"
    git tag -a YYYY-Week -m "Automated weekly tag: `date +%Y-%W`"
    git push
    git push --tags
    # grab a list of the files that were changed
    FILES=`git show --pretty="format:" --name-only HEAD`
    if [ -z $FILES ]; then
        log_to_olog "No untracked or uncommitted files found in the ipython configuration. Yay!" "DAMA Software"
    else
        log_to_olog "The following files were found in the ipython configuration: $FILES" "DAMA Software"
    popd
    exit

2. Write the current state of the collection environment ::

    conda_envs_path="/opt/conda_envs"
    previous_collection_name=`ls -r $conda_envs_path | grep collection | head -n2 | tail -n1`
    conda list -p $conda_envs_path/$previous_collection_name > /opt/conda/envs_list/previous_collection_name--END
    mkdir -p /opt/conda/envs_list
    pushd /opt/conda/envs_list
    if [ -s ${previous_collection_name}--START ]; then
        diff ${previous_collection_name}--START ${previous_collection_name}--END > ${previous_collection_name}--DIFF
        if [ -s ${previous_collection_name}--DIFF ]; then
            # notify the slack channel that the environments are different
            notify_slack \
                "Collection+Environment+Changed:+{{ BEAMLINE_USER }}" \
                `cat /opt/conda/envs_list/${previous_collection_name}--DIFF` \
                "#automated-deployment"
        fi
    else
        # notify the slack channel that there is no previous environment list to compare
        notify_slack \
            "No+Previous+Environment+List:+{{ BEAMLINE_USER }}" \
            `ls /opt/conda/envs_list/` \
            "#automated-deployment"
    fi

3. Create new conda collection environment at BEAMLINE_WORKSTATION with the
   following command ::

    new_collection_name=collection-`date +%Y-%W`
    conda create -p /opt/conda_envs/$new_collection_name COLLECTION_{{ BEAMLINE }} --override-channels -c anaconda -c nsls2-{{ BEAMLINE }}
    # export the list of the new packages
    conda list -p /opt/conda/envs/$new_collection_name > /opt/conda/envs_list/${new_collection_name}--START

    # log that this conda collection environment was created
    log_to_olog "New collection environment created at /opt/conda/envs/$new_collection_name" "DAMA Software"

4. Update the collection launching script to point to /opt/conda_envs/collection-YEAR-WEEK_OF_YEAR ::

    echo "#! /bin/bash
    source activate /opt/conda_envs/collection-`date +%Y-%W`"
    ipython --profile=collection --profile_dir=/home/{{ BEAMLINE_USER }}/ipython_profile
    " > /bin/bs.sh

6. **(Manual step)** Run UAT with the beamline staff.  If UAT fails, fix the
   problems on the spot or copy the stack trace to https://github.com/NSLS-II/Bug-Reports/issues
   and roll back the symlink so that it points at /opt/conda_envs/collection-YEAR-(WEEK-1)
