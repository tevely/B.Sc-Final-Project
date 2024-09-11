from datetime import date
import json
import operator

from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
from sqlalchemy import create_engine

from analyze_data import find_best
import utils
import plotting
import doubletrack


import os
os.chdir(os.path.dirname(__file__))
matlab = utils.start_matlab()

# %%
db = create_engine("sqlite:///../data/doubletrack.db")
df = pd.read_sql_table("experiments", db)
df = df.round({"dn_track": 3})
# df = df.loc[df.record_created.apply(operator.methodcaller("date")) != date(2024, 5, 7)]
best = find_best(df)
# %% Best interaction effective area
wl = 0.405
dn = -0.005
best[wl][dn]["A_I"]["params"]["npml"] = 5
best[wl][dn]["A_I"]["params"]["space_x"] = 15
best[wl][dn]["A_I"]["params"]["nmodes"] = 30

result = doubletrack.simulate(
    best[wl][dn]["A_I"]["params"], wl_pump=wl, engine=matlab
)
fig, ax = plotting.plot_s_i_p_modes(
    result, op=np.abs, logscale=True, contour=True, cmap="inferno"
)
A_I = utils.interaction_eff_area(result)
fig.suptitle(
    r"$\lambda_p$={:.0f} nm, $\Delta n$={}. $A_I$={:.0f} um${{}}^2$"
    .format(1e3 * wl, dn, A_I)
)
plt.show()
# %% Best pump coupling
wl = 0.405
dn = -0.004
best[wl][dn]["eta_p"]["params"]["space_x"] = 10
best[wl][dn]["eta_p"]["params"]["nmodes"] = 20
result = doubletrack.simulate(
    best[wl][dn]["eta_p"]["params"], wl_pump=wl, engine=matlab
)
fig, ax = plotting.plot_s_i_p_modes(
    result, op=np.abs, logscale=True, contour=True, cmap="inferno"
)
fig.suptitle(
    r"$\lambda_p$={:.0f} nm, $\Delta n$={}. $\eta_p$={:.2f}"
    .format(1e3 * wl, dn, best[wl][dn]["eta_p"]["value"])
)
plt.show()