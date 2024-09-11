from cycler import cycler
import numpy as np
from matplotlib import pyplot as plt

import utils


def plot_stats(df, x, y, categorical="dn_track", ax=None):
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = plt.gcf()
    categories = np.sort(df[categorical].unique())
    for _ in set(df[categorical]):
        dfi = df.loc[_ == df[categorical]]
        ax.scatter(
            dfi[x], dfi[y],
            label=r"{}={:g}".format(categorical, _)
        )
    ax.legend()
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    return fig, ax


def plot_s_i_p_modes(
        result,
        op=None, logscale=False, vmin=None, vmax=None, cmap=None, contour=False
):
    if len(result) == 5:
        x, y, E_s, E_i, E_p = result
    else:
        x = result["signal"]["xc"].real.ravel()
        y = result["signal"]["yc"].real.ravel()
        E_s = result["signal"]["Ex"]
        E_i = result["idler"]["Ey"]
        E_p = result["pump"]["Ex"]
    if op is None:
        if logscale:
            op = abs
        else:
            op = np.real
    fig, ax = plt.subplots(
        1, 3, figsize=(12, 5), sharey=True, sharex=True
    )
    E_s = op(E_s)
    E_i = op(E_i)
    E_p = op(E_p)
    Us = E_s / np.sqrt(utils.norm(x, y, E_s))
    Ui = E_i / np.sqrt(utils.norm(x, y, E_i))
    Up = E_p / np.sqrt(utils.norm(x, y, E_p))
    if vmax is None:
        if logscale:
            vmax = 0
        else:
            vmax = max(np.max(abs(Us)), np.max(abs(Ui)), np.max(abs(Up)))
    if vmin is None:
        if logscale:
            vmin = -30
        else:
            vmin = min(np.min(Us), np.min(Ui), np.min(Up))
    ax[0].set_title('Signal (H)')
    ax[1].set_title('Idler (V)')
    ax[2].set_title('Pump (H)')
    
    for i, U in enumerate([Us, Ui, Up]):
        Umax = np.max(np.abs(U))
        levels = np.array([Umax / np.e])
        if logscale:
            U = 10 * np.log10(1e-15 + abs(U))
            levels = 10 * np.log10(1e-15 + levels)
        im = ax[i].pcolormesh(x, y, U.T, vmin=vmin, vmax=vmax, cmap=cmap)
        if contour:
            labels = ["1/$e^2$"]
            cs = ax[i].contour(x, y, U.T, levels=levels, colors="white")
            fmt = {}
            for l, s in zip(cs.levels, labels):
                fmt[l] = s
            cl = ax[i].clabel(cs, inline=True, fmt=fmt)
        ax[i].set_xlabel('x [um]')
        ax[i].set_ylabel('y [um]')
    cb = fig.colorbar(im, ax=ax, location="bottom", fraction=0.05)

    if logscale:
        cb.set_label("dB")
    return fig, ax


def plot_signal_spectrum(result, bandwidth, pump_power, nl_coeff, length, poling_period, ax=None):
    int_eff_area = utils.interaction_eff_area(result) * 1e-12
    n_s = result["signal"]["neff"]
    n_i = result["idler"]["neff"]
    n_p = result["pump"]["neff"]
    wl_p = result["pump"]["wl"] * 1e-6
    wl_s = result["signal"]["wl"] * 1e-6
    wls = np.linspace(wl_s - bandwidth / 2, wl_s + bandwidth / 2, 300)
    spectrum = utils.spectral_density(
        int_eff_area, n_s, n_i, n_p, wl_p, wls,
        nl_coeff, length, pump_power, poling_period
    )
    pair_rate = utils.pair_rate(
        int_eff_area, n_s, n_i, n_p, wl_p, wls,
        nl_coeff, length, pump_power, poling_period
    )
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = plt.gcf()
    ax.plot(wls * 1e9, spectrum * 1e3)
    ax.set_ylabel("Spectral Density [pW/nm]")
    ax.set_xlabel("Wavelength [nm]")
    ax.set_title("SPDC Efficiency")
    ax.grid(True)
    ax.text(
        0, -0.2,
        "Generation Rate = {:.1f} Mpair/s at 1 mW transmitted pump\n"
        "Poling period = {:.1f} um".format(pair_rate * 1e-6, poling_period * 1e6),
        va="top",
        transform=ax.transAxes
    )
    return fig, ax


def prop_cycle(length):
    prop_cycle = plt.rcParams['axes.prop_cycle']
    colors = prop_cycle.by_key()['color'][:length]
    cyc = cycler(marker=['o', 's', '^', "D"],
                 color=colors,
                 linestyle=["-", "--", "-.", "dotted"])
    return cyc

