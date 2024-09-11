import io
import os
import subprocess
import sys
import uuid

import matlab.engine
import numpy as np
import scipy.integrate
import scipy.interpolate
from scipy.io import loadmat
import scipy.constants


def start_matlab():
    eng = matlab.engine.start_matlab()
    eng.cd(os.path.dirname(__file__))
    eng.addpath("matlab_src")
    return eng


def run_matlab(command: str, args: dict, engine=None):
    filename = os.path.abspath(
        os.path.join("..", "data", uuid.uuid4().hex + ".mat")
    )
    try:
        if engine is not None:
            engine.clear("all", nargout=0)
            engine.workspace["filename"] = filename
            for key, val in args.items():
                engine.workspace[key] = val
            out = io.StringIO()
            err = io.StringIO()
            engine.run(command, nargout=0, stdout=out, stderr=err)
        else:
            matlab_vars = "filename='{}';".format(filename)
            for key, val in args.items():
                matlab_vars += "{}={}; ".format(key, val)
            call_args = [
                "matlab", "-singleCompThread",
                "-batch", matlab_vars + command + "; exit"
            ]
            with open("../data/run_matlab.log", "w") as f:
                subprocess.check_call(
                    call_args,
                    stdout=f,
                    stderr=f,
                    cwd="matlab_src"
                )
        result = loadmat(filename)
    except Exception as e:
        raise e
    finally:
        os.remove(filename)
    return result


def get_modes(result):
    x = result["signal"]["xc"].ravel()
    y = result["signal"]["yc"].ravel()
    shape = (len(x), len(y))
    Es = result["signal"]["Ex"].real.reshape(*shape)
    Ei = result["idler"]["Ey"].real.reshape(*shape)
    Ep = result["pump"]["Ex"].real.reshape(*shape)
    return x, y, Es, Ei, Ep


def norm(x, y, data):
    I1 = scipy.integrate.simpson(np.abs(data) ** 2, y)
    res = scipy.integrate.simpson(I1, x)
    return res


def coupling_efficiency(xin, yin, Ein, xout, yout, Eout):
    # Resampling Eout to (xin, yin) grid
    Eout_re = scipy.interpolate.RectBivariateSpline(xout, yout, Eout.real, kx=1, ky=1)(xin, yin)
    Eout_im = scipy.interpolate.RectBivariateSpline(xout, yout, Eout.imag, kx=1, ky=1)(xin, yin)
    Eout = Eout_re + 1j * Eout_im
    I1 = scipy.integrate.simpson(Ein * Eout.conj(), yin)
    I2 = np.abs(scipy.integrate.simpson(I1, xin)) ** 2
    I3 = norm(xin, yin, Ein)
    I4 = norm(xin, yin, Eout)
    return I2 / (I3 * I4)


def interaction_eff_area(*args):
    if len(args) == 1:
        result = args[0]
        x = result["signal"]["xc"].real.ravel()
        y = result["signal"]["yc"].real.ravel()
        Es = result["signal"]["Ex"].real
        Ei = result["idler"]["Ey"].real
        Ep = result["pump"]["Ex"].real
    else:
        x, y, Es, Ei, Ep = args
    Us = Es / np.sqrt(norm(x, y, Es))
    Ui = Ei / np.sqrt(norm(x, y, Ei))
    Up = Ep / np.sqrt(norm(x, y, Ep))
    I1 = scipy.integrate.simpson(Up * Us.conj() * Ui.conj(), y)
    I2 = scipy.integrate.simpson(I1, x)
    res = 1 / I2 ** 2
    return res


def poling_period(*args):
    if len(args) == 1:
        result = args[0]
        n_s = result["signal"]["neff"]
        n_i = result["idler"]["neff"]
        n_p = result["pump"]["neff"]
        wl_p = result["pump"]["wl"]
        wl_s = result["signal"]["wl"]
    else:
        wl_p, wl_s, n_s, n_i, n_p = args
    wl_i = wl_s * wl_p / (wl_s - wl_p)
    return 1 / (n_p.real / wl_p - n_s.real / wl_s - n_i.real / wl_i)


def spectral_density(A_I, n_s, n_i, n_p, wl_p, wl_s, d, L, power_p, Lambda):
    n_s = n_s.real
    n_i = n_i.real
    n_p = n_p.real
    const = 16 * np.pi ** 3 * scipy.constants.hbar * scipy.constants.c /\
        scipy.constants.epsilon_0
    wl_i = wl_s * wl_p / (wl_s - wl_p)
    amplitude = L**2 * d**2 * power_p / (n_s * n_i * n_p * wl_s ** 4 * wl_i * A_I)
    delta_k = 2 * np.pi * (n_p / wl_p - n_s / wl_s - n_i / wl_i - 1 / Lambda)
    res = const * amplitude * np.sinc(delta_k * L / 2) ** 2
    return res


def pair_rate(A_I, n_s, n_i, n_p, wl_p, wl_s, d, L, power_p, Lambda):
    spectrum = spectral_density(A_I, n_s, n_i, n_p, wl_p, wl_s, d, L, power_p, Lambda)
    photon_energy = (scipy.constants.h * scipy.constants.c / wl_s)
    rate = np.trapz(spectrum / photon_energy, wl_s)
    return rate


def peneration_depth(x, y, E):
    i, j = np.unravel_index(np.argmax(abs(E)), E.shape)
    Emax = E[i, j]
    iEe = np.argmin(abs(E[i, :] - Emax / np.e))
    mode_radius = np.abs(y[iEe] - y[j])
    xc = x[i]
    yc = y[j]
    return xc, yc, mode_radius 


def df2db(df, db_path):
    from hyperopt import STATUS_OK
    from experiments import Experiments
    from sqlalchemy import create_engine
    engine = create_engine("sqlite:///" + db_path)
    db = Experiments(engine)
    for i in df.index:
        row = df.iloc[i]
        params = row["params"]
        params["dn_halo"] = -params["dn_track"] / 4
        params["wl_pump"] = row["wl_pump"]
        params["wl_pump"] = row["wl_pump"]
        result = {
            "wl_pump": row["wl_pump"],
            "wl_signal": row["wl_signal"],
            "neff_signal": row["neff_signal"],
            "neff_idler": row["neff_idler"],
            "neff_pump": row["neff_pump"],
            "wl_idler": row["wl_idler"],
            "int_eff_area": row["int_eff_area"],
            "coupling_s": row["coupling_s"],
            "coupling_i": row["coupling_i"],
            "coupling_p": row["coupling_p"],
            "status": STATUS_OK,
            "start_time": row["eval_time"],
            "duration": row["duration"],
        }
        db.record_experiment(params, result)
