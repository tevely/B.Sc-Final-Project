import plotting
import utils
import optimize
from config import DATA_DIR
import json
from glob import glob
import pickle
import shutil

import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from tqdm import tqdm
from sqlalchemy import create_engine

import os
os.chdir(os.path.dirname(__file__))


matlab = None


def find_best(df):
    columns = [
        "dn_track",
        "dn_halo",
        "track_w",
        "track_h",
        "gap",
        "space_x",
        "dx",
        "npml",
        "wl_pump",
        "wl_signal"
    ]
    best = {}
    for wl in df.wl_pump.unique():
        best[wl] = {}
        for dn in np.sort(df.dn_track.unique()):
            dfi = df.loc[df.dn_track == dn].loc[df.wl_pump == wl]
            ibest_A_I = dfi["int_eff_area"].argmin()
            ibest_eta_p = dfi["coupling_p"].argmax()
            best_A_I = dfi.iloc[ibest_A_I]
            best_eta_p = dfi.iloc[ibest_eta_p]
            best[wl][dn] = {
                "A_I": {
                    "params": best_A_I[columns].to_dict(),
                    "value": best_A_I["int_eff_area"],
                },
                "eta_p": {
                    "params": best_eta_p[columns].to_dict(),
                    "value": best_eta_p["coupling_p"],
                },
            }
    return best


# %% Load data
if __name__ == "__main__":
    db = create_engine("sqlite:///../data/doubletrack.db")
    # %% Interaction effective area vs gap
    df = pd.read_sql_table("experiments", db)
    max_A_I = 500
    dfp = df.loc[df.int_eff_area < max_A_I]
    fig, ax = plt.subplots(1, 2, figsize=(7, 4), sharey="row")
    for i, wl in enumerate(dfp.wl_pump.unique()):
        for dn in np.sort(dfp.dn_track.unique()):
            dfpi = dfp.loc[dn == dfp.dn_track].loc[dfp.wl_pump == wl]
            ax[i].scatter(
                dfpi["gap"], dfpi["int_eff_area"],
                label=r"dn={}$\times 10^{{-3}}$".format(1e3 * dn)
            )
        ax[i].set_title(r"$\lambda_p$={:.0f} nm".format(wl * 1e3))
        ax[i].set_xlabel("Gap [um]")
        ax[i].set_ylabel("$A_I$ [um${}^2$]")
    ax[0].legend()
    # %% Interaction effective area vs dn
    df = pd.read_sql_table("experiments", db)
    fig, ax = plt.subplots()
    for wl in df.wl_pump.unique():
        data = df.loc[df.wl_pump == wl].groupby(
            "dn_track")["int_eff_area"].min()
        ax.plot(-data.index * 1e3, data.values,
                "o-",
                label=f"$\lambda_p$={1e3*wl:.0f} nm")
    ax.legend()
    ax.grid(True)
    ax.set_title("Interaction Effective Area")
    ax.set_xlabel("$\Delta n\\times 10^3$")
    ax.set_ylabel("$A_I$ [um${}^2$]")
    # %% Coupling loss vs dn
    df = pd.read_sql_table("experiments", db)
    df = df.round({"dn_track": 3})
    fig, ax = plt.subplots()
    for wl in df.wl_pump.unique():
        data = df.loc[df.wl_pump == wl].groupby("dn_track")["coupling_p"].max()
        loss = -10 * np.log10(data.values)
        ax.plot(-data.index * 1e3, loss,
                   marker="^",
                   linestyle="-",
                   label=f"Pump $\lambda_p$={1e3*wl:.0f} nm")
    for wl in df.wl_signal.unique():
        data = df.loc[df.wl_signal == wl].groupby("dn_track")["coupling_s"].max()
        loss = -10 * np.log10(data.values)
        ax.plot(-data.index * 1e3, loss,
                   marker="s",
                   linestyle="-",
                   label=f"Signal, $\lambda_s$={1e3*wl:.0f} nm")
    ax.legend()
    ax.grid(True)
    ax.set_title("Coupling Loss")
    ax.set_xlabel("$\Delta n\\times 10^3$")
    ax.set_ylabel("Coupling loss [dB]")
    # %%
    dfp = df.loc[df.int_eff_area < max_A_I]
    fig, ax = plt.subplots(1, 2, figsize=(8, 4))
    for i, (wl, dfi) in enumerate(dfp.groupby("wl_pump")):
        plotting.plot_stats(dfi, "track_h", "int_eff_area",
                            "dn_track", ax=ax[i])
        ax[i].set_title(r"$\lambda_p$={:.0f} nm".format(wl * 1e3))
        ax[i].set_xlabel("track height [um]")
        ax[i].set_ylabel("$A_I$ [um${}^2$]")
    # %%
    fig, ax = plt.subplots()
    dfp = df.loc[df.int_eff_area < max_A_I]
    idx = dfp["int_eff_area"].argsort()[::-1]
    ax.scatter(
        dfp["gap"].to_numpy()[idx],
        np.abs(dfp["track_h"].to_numpy()[idx]),
        c=dfp["int_eff_area"].to_numpy()[idx],
        s=4
    )
    ax.set_xlabel("gap [um]")
    ax.set_ylabel("track height [um]")
    # %%
    fig, ax = plt.subplots()
    dfp = df.loc[df.int_eff_area < max_A_I]
    idx = dfp["int_eff_area"].argsort()[::-1]
    ax.scatter(
        dfp["gap"].to_numpy()[idx],
        np.abs(dfp["dn_track"].to_numpy()[idx]) * 1e3,
        c=dfp["int_eff_area"].to_numpy()[idx]
    )
    ax.set_xlabel("gap [um]")
    ax.set_ylabel("$\Delta n\\times 10^3$")
