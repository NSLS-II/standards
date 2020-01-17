# -*- coding: utf-8 -*-
"""
Automatically show integrate S(q) during data collection
********************************************************

Problem
=======

As 2D diffraction images are collected, extract and plot the intgrated
:math:`S(q)`.

Approach
========

Write a callback which on each event:

  - uses filestore to retrieve the full image
  - uses :class:`~skbeam.core.accumulators.binned_statistic.RadialBinnedStatistic` to
    compute

Example Solution
================

The :func:`bluesky.plans.adaptive_scan` aims to maintain a certain delta in y
between successive steps through x. After each step, it accounts for the local
derivative and adjusts it step size accordingly. If it misses by a large
margin, it takes a step backward (if allowed).

"""


import matplotlib.pyplot as plt
from bluesky import RunEngine
from bluesky.examples import Mover, ReaderWithFileStore, ReaderWithFSHandler
import bluesky.plans as bp
from bluesky.callbacks import CallbackBase
import portable_fs.sqlite.fs as psf
import os
import numpy as np
import skbeam.core.accumulators.binned_statistic as scabs
import portable_mds.sqlite.mds as psm
import databroker

###############################################################################
# Setup synthetic Broker, motor, and detector
# -------------------------------------------
#
# The image is
#
# .. math::
#
#    T*\left|\sin\left(R/5)\right)\right|*\exp\left({\frac{-R^2}{10}}\right)
#
# where :math:`T` is the temperature and :math:`R` is distance from the origin

mds = psm.MDS({'directory': '/tmp/pmds'})
fs = psf.FileStore({'dbpath': '/tmp/fs1'})
fs.register_handler('RWFS_NPY', ReaderWithFSHandler, overwrite=True)
db = databroker.Broker(mds, fs)
os.makedirs('/tmp/fake_data', exist_ok=True)

temp = Mover('T', {'T': lambda x: x}, {'x': 0})

X, Y = np.ogrid[-53:54, -50:51]
R = np.hypot(X, Y) / 5
base = np.exp(- R*R / 70) * np.abs(np.sin(R))


def synthetic_data():
    return temp.read()['T']['value'] * base


det = ReaderWithFileStore('det', {'image': synthetic_data},
                          fs=fs, save_path='/tmp/fake_data')


# Do this if running the example interactively;
# skip it when building the documentation.
if 'BUILDING_DOCS' not in os.environ:
    from bluesky.utils import install_qt_kicker  # for notebooks, qt -> nb
    det.exposure_time = 1
    temp._fake_sleep = 1
    install_qt_kicker()
    plt.ion()


###############################################################################
# The callback object
# -------------------
#

class LiveIntegrate(CallbackBase):
    SMALL = 1e-6

    def __init__(self, name, ax=None, bins=100):
        if ax is None:
            ax = plt.gca()
        ax.set_xlabel('$q$')
        ax.set_ylabel('$s(q)$')
        self.ax = ax
        self._name = name
        self._bins = bins
        self.binner = None
        self.wl = 1
        self.center = None

    def start(self, doc):
        # pull wave length data from the start document
        self.wl = doc.get('wavelength', self.wl)
        # extract the center from the start document
        self.center = doc.get('center', None)
        # extract the uid and sample from the start document
        self.ax.set_title('[{uid:.6}]: {sample}'.format(
            **doc))

    def descriptor(self, doc):
        # pull the image size data from the descriptor
        dk = doc['data_keys'][self._name]
        # set up the binning
        self.binner = scabs.RadialBinnedStatistic(dk['shape'], bins=100,
                                                  origin=self.center)

    def event(self, doc):
        # go to filestore to get the raw image back
        image = db.fs.retrieve(doc['data'][self._name])
        # bin the image
        ret = self.binner(image)
        # scale the pixel position by wavelength
        centers = self.binner.bin_centers / self.wl
        # plot the integrated data, label with temperature
        self.ax.plot(centers, ret,
                     label='{} K'.format(doc['data']['T']))
        # update the legend
        self.ax.legend()
        # ask the graph to redraw the next time it is convenient
        self.ax.figure.canvas.draw_idle()


###############################################################################
# Set up the :class:`~bluesky.run_engine.RunEngine` and some configuration data
# -----------------------------------------------------------------------------

RE = RunEngine({})
RE.md['wavelength'] = 15
RE.md['center'] = [107/2, 101/2]
RE.subscribe('all', mds.insert)

RE(bp.scan([det], temp, 200, 270, 5), LiveIntegrate('image', None),
   sample='FooBar')
