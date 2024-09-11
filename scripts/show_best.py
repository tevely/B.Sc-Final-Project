import json

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


# %%
db = create_engine("sqlite:///../data/doubletrack.db")
df = pd.read_sql_table("experiments", db)
df = df.round({"dn_track": 3})
best = find_best(df)
filename = "../data/doubletrack-best.json"
with open(filename, "w") as f:
    json.dump(best, f, indent=1)
# %% Best geometry
df = pd.read_sql_table("experiments", db)
from datetime import date
import operator
# df = df.loc[df.record_created.apply(operator.methodcaller("date")) != date(2024, 5, 7)]
df = df.round({"dn_track": 3})
best = find_best(df)
cyc = plotting.prop_cycle(4)
axlabels='abcd'
fig, ax = plt.subplots(3, 1, figsize=(8, 9), sharex="col", gridspec_kw=dict(hspace=0.4))
for ax_ in ax:
    ax_.set_prop_cycle(cyc)
params = ["gap", "track_w", "track_h"]
pretty = ["gap [um]", "$w$ [um]", "$h$ [um]"]
for wl in best:
    dn_track = np.sort(list(best[wl].keys()))
    for i, (param, ylabel) in enumerate(zip(params, pretty)):
        for metric in ["A_I", "eta_p"]:
            label = (r"Best ${}$. $\lambda_p$={:.0f} nm".format(
                metric.replace("eta_p", "\eta_p"), wl * 1e3)
            )
            values = [best[wl][dn][metric]["params"][param] for dn in dn_track]
            ax[i].plot(-dn_track * 1e3, values, label=label)
            ax[i].set_xlabel("$\Delta n\\times 10^3$")
            ax[i].set_ylabel(ylabel)
            ax[i].set_title(f"({axlabels[i]})", position=(-0.05, 0))
            ax[i].legend(loc="upper right")
            ax[i].grid(True)
fig.suptitle("Optimized parameters", fontsize=14, position=(0.5, 0.93))
# %%
fig, ax = plt.subplots(2, 2, figsize=(10, 9), gridspec_kw=dict(hspace=0.3))
for i, metric in enumerate(["A_I", "eta_p"]):
    for j, wl in enumerate(best):
        dn_track = np.sort(list(best[wl].keys()))
        gap = [best[wl][dn][metric]["params"]["gap"] for dn in dn_track]
        track_w = [best[wl][dn][metric]["params"]["track_w"] for dn in dn_track]
        track_h = [best[wl][dn][metric]["params"]["track_h"] for dn in dn_track]
        ax[i, j].plot(-dn_track * 1e3, gap, "o-", label="Gap [um]")
        ax[i, j].plot(-dn_track * 1e3, track_w, "s-", label="Track Width [um]")
        ax[i, j].plot(-dn_track * 1e3, track_h, "^-", label="Track Height [um]")
        ax[i, j].set_title(r"Best ${}$. $\lambda_p$={:.0f} nm".format(
            metric.replace("eta_p", "\eta_p"), wl * 1e3)
        )
        ax[i, j].set_xlabel("$\Delta n\\times 10^3$")
        ax[i, j].legend()
        ax[i, j].grid(True)
fig.suptitle("Optimized parameters")
# %%
with open("../data/overlaps.json", "r") as f:
    overlaps = json.load(f)
 
wls = list(overlaps.keys())
dns = list(overlaps[wls[0]])
length = np.linspace(50, 1000, len(overlaps[wls[0]][dns[0]]))
fig, ax = plt.subplots(1, 2)
for i, wl in enumerate(wls):
    for dn in dns:
        ols = np.array(overlaps[wl][dn])
        i0 = np.argmax(np.sum(ols, axis=0))
        ax[i].plot(length, ols[:, i0])
# %%
ibest = {}
vbest = {}
for wl in overlaps:
    ibest[wl] = {}
    vbest[wl] = {}
    for dn in overlaps[wl].keys():
        ols = np.array(overlaps[wl][dn])
        i0 = np.argmax(np.sum(ols, axis=0))
        ibest[wl][dn] = np.argmax(ols[:, i0])
        vbest[wl][dn] = np.max(ols[-1, i0])

dn_track = np.array([
    float(key.replace("x_", "").replace("_", "."))
    for key in overlaps[wl].keys()
])
from cycler import cycler

cyc = (cycler(marker=['o', 's', '^', "D"]) +
       cycler(color=["k", "r", "b", "y"]))
fig, axs = plt.subplots(1, 2, figsize=(10, 4))
ax = axs[0]
ax.set_prop_cycle(cyc)
for wl in overlaps:
    ydata = 10 * np.log10(list(vbest[wl].values()))
    ax.plot(dn_track * 1e3, ydata, label=wl)
ax.grid(True)
ax.set_title("(a)", position=(0, 0))
ax.set_xlabel("$\Delta n\\times 10^3$")
ax.set_ylabel("Insertion Loss [dB]")
ax.legend(["$\lambda_p$=405 nm", "$\lambda_p$=775 nm"])

ax = axs[1]
ax.set_prop_cycle(cyc)
for wl in overlaps:
    ydata =  [length[i] for i in ibest[wl].values()]
    # ydata[3] = np.nan
    ax.plot(dn_track * 1e3, ydata, label=wl)
ax.grid(True)
ax.legend(["$\lambda_p$=405 nm", "$\lambda_p$=775 nm"])
ax.set_xlabel("$\Delta n\\times 10^3$")
ax.set_ylabel("Taper Length [um]")
ax.set_title("(b)", position=(0, 0))

