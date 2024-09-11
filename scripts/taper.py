import json
import os
import time

import numpy as np
import matlab.engine
from matplotlib import pyplot as plt
import pandas as pd
from sqlalchemy import create_engine


def simulate(params, engine: matlab.engine.MatlabEngine):
    crystal_axes = [2, 3, 1]
    eps_bg = engine.epsKTPkato(params["wl"], crystal_axes[params["pol"] + 1])
    params["n_background"] = np.sqrt(eps_bg)
    params["n_0"] = params["n_background"] + params["dn_halo"]
    P = engine.taper(params, True)
    engine.workspace["P"] = P
    overlaps = np.asarray(eng.eval("P.modeOverlaps"))
    return overlaps


if __name__ == "__main__":
    wl = 0.775
    dn_track = -4e-3
    pol = 1
    db = create_engine("sqlite:///../data/doubletrack.db")
    df = pd.read_sql_table("experiments", db)
    with open("hp_space.json", "r") as f:
        hp_space = json.load(f)
    beam_radius = hp_space["r_in"][str(wl)]
    df = df.loc[df.wl_pump == wl].loc[df.dn_track == dn_track]
    ietap = df["coupling_p"].argmax()
    iai = df["int_eff_area"].argmin()
    dn_halo = df.iloc[iai].dn_halo
    gap_in = df.iloc[ietap].gap
    gap_out = df.iloc[iai].gap
    track_w_in = df.iloc[ietap].track_w
    track_w_out = df.iloc[iai].track_w
    track_h_in = df.iloc[ietap].track_h
    track_h_out = df.iloc[iai].track_h
    space_x = df.iloc[iai].space_x
    space_y = df.iloc[iai].space_y
    dx = df.iloc[iai].dx
    dy = df.iloc[iai].dy
    dz = 1
    Nz = 500
    nmodes = 10 # df.iloc[iai].nmodes
    updates = 50
    boundary = "0000"
    npml = df.iloc[iai].npml
    input_length = 0.01
    tp_length = 500
    total_length = 1000
    params = {
        "wl": wl,
        "dn_track": dn_track,
        "dn_halo": dn_halo,
        "beam_radius": beam_radius,
        "gap_in": gap_in,
        "gap_out": gap_out,
        "track_w_in": track_w_in,
        "track_w_out": track_w_out,
        "track_h_in": track_h_in,
        "track_h_out": track_h_out,
        "boundary": boundary,
        "npml": npml,
        "input_length": float(input_length),
        "tp_length": float(tp_length),
        "total_length": float(total_length),
        "space_x": space_x,
        "space_y": space_y,
        "dx": dx,
        "dy": dy,
        "dz": dz,
        "Nz": Nz,
        "pol": pol,
        "nmodes": nmodes,
        "updates": updates
    }
    print("Starting matlab engine")
    eng = matlab.engine.start_matlab()
    eng.cd(os.path.abspath(os.path.dirname(__file__)))
    eng.addpath("matlab_src")
    # %%
    t0 = time.time()
    result = simulate(params, engine=eng)
    t1 = time.time()
    print("Elapsed time: %.3f s" % (t1 - t0))
    eng.exit()
    # %%
    fig, ax = plt.subplots()
    z = np.linspace(0, total_length, result.shape[1])
    ax.plot(z, result.T)
    ax.grid(True)
    ax.set_title("Mode Converter Performance")
    ax.set_xlabel("z [um]")
    ax.set_ylabel("Mode Overlap")
    ax.set_yscale("log")
    ax.legend([f"Mode {i+1}" for i in range(result.shape[0])])