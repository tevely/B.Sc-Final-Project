# -*- coding: utf-8 -*-
"""
Created on Sun Apr  7 17:14:16 2024

@author: fedarm
"""

import os
import subprocess

import utils


args = {
    "dn": 0.02,
    "width": 4e-6,
    "wl_pump": 775e-9,
    "space_x": 4e-6,
    "ymin": -10e-6,
    "ymax": 2e-6,
    "dx": 0.1e-6,
}
result = utils.run_matlab("fiorentino", args)
# %%
mode = "signal"
x = result[mode]["x"].ravel() * 1e6
y = result[mode]["y"].ravel() * 1e6

from matplotlib import pyplot as plt
fig, ax = plt.subplots(1, 2, dpi=150, sharey="row")
fig.suptitle(mode.capitalize())
for i, field in enumerate(["Hx", "Hy"]):
    ax[i].pcolormesh(x, y, result[mode][field].T.real, cmap="jet")
    ax[i].set_title(field)
    ax[i].set_xlabel("x [um]")
    ax[i].set_ylabel("y [um]")
