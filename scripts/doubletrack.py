# -*- coding: utf-8 -*-
"""
Created on Sun Apr  7 17:14:16 2024

@author: fedarm
"""
import os
import time

import numpy as np
import matlab.engine
import utils
import plotting


def simulate(params, wl_pump, engine: matlab.engine.MatlabEngine):
    result = {}
    dn_halo = -params["dn_track"] / 4
    params["dn_halo"] = dn_halo
    params["space_y"] = params["space_x"]
    params["dy"] = params["dx"]
    result["params"] = params
    cryst_ax = [1, 2, 0]
    modes = ["signal", "idler", "pump"]
    pol_pump = 0
    wl = dict(zip(modes, [2 * wl_pump, 2 * wl_pump, wl_pump]))
    pol = dict(zip(modes, [pol_pump, (pol_pump + 1) % 2, pol_pump]))
    
    for mode in modes:
        result[mode] = engine.doubletrack(params, wl[mode], pol[mode] + 1)
        for key, val in result[mode].items():
            if isinstance(val, matlab.double):
                result[mode][key] = np.array(val)
        result[mode]["wl"] = wl[mode]
    return result


if __name__ == "__main__":
    dn_track = -0.004
    track_w = 2.8
    track_h = 17
    gap = 8.2
    space_x = 15
    dx = 0.2
    npml = 5
    wl_pump = 0.405
    nmodes = 10
    params = {
        "dn_track": float(dn_track),
        "track_w": float(track_w),
        "track_h": float(track_h),
        "gap": float(gap),
        "space_x": float(space_x),
        "dx": float(dx),
        "npml": npml,
        "nmodes": nmodes,
    }
    print("Starting matlab engine")
    eng = matlab.engine.start_matlab()
    eng.cd(os.path.abspath(os.path.dirname(__file__)))
    eng.addpath("matlab_src")
    t0 = time.time()
    result = simulate(params, wl_pump, engine=eng)
    eng.exit()
    t1 = time.time()
    print("Elapsed time: %.3f s" % (t1 - t0))
    # %%
    plotting.plot_s_i_p_modes(result, op=np.abs, contour=True, cmap="inferno")
    # %%
    d24 = 7.6e-12  # relevant KTP nonlinear coefficient [W / V]
    d = 2 * d24 / np.pi  # effective nonlinear coefficient
    power_p = 1e-3  # pump power [W]
    L = 10e-3  # waveguide length [m]
    poling_period = utils.poling_period(result)
    bandwidth = 1e-9  # pump filter bandwidth [m]
    fig, ax = plotting.plot_signal_spectrum(
        result, bandwidth, power_p, d, L, poling_period * 1e-6
    )
