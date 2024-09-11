#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
os.environ["OMP_NUM_THREADS"] = "1"

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
from vpipda.material import *
from vpipda import layout as l2d, units
from vpipda.layout import layout3d as l3d
from vpipda import device as dev
from vpipda import bpm
from vpipda import mode
from materials_vpidd import KTP
from double_track import double_track_wg

import vpipda
vpipda.config.tempdir = "../data"
plt.rc('figure', dpi=100)


bulk_mat = KTP(0)
dn_track = -1e-3
dn_halo = 2e-4
length = 1000
track_w = 3
track_h = 18
halo_w = halo_h = track_h
width = 15
space = (30, 30)
dx = 0.2
dy = dx
dz = 2
wl = 2 * 404.85 * units.nm
xs = double_track_wg(
    bulk_mat, dn_track, dn_halo, track_w, track_h, halo_w, halo_h, width
)

# %%
def get_layout(z):
    return xs

device = dev.Straight(get_layout, length, width)
sim = bpm.SolverBPM(device)
sim.get_layout = get_layout
sim.z_uniform = True
sim.mesh.box = sim.layout.box.expand(*space, 0)
sim.mesh.box = sim.mesh.box.modify(xmin=0, ymin=0)
sim.mesh.update(dx=dx, dy=dy, dz=dz)

for side in ["xmax", "ymax"]:
    sim.mesh.set_boundary(side, "PML", depth=20, freq=str(wl), damping=1e-80)

# sim.mesh.slice(y=0).plot()
print(sim.mesh.shape)
# print("Memory per ScalarField3D: {:.0f} MB".format(np.product(sim.mesh.shape) * 128 / 8 / 1024 ** 2))

from vpipda.mode import gauss_beam

waist = 7
pol = "TM"
launch_field = [
    # gauss_beam(KTP, wl, waist, pol="TE"),
    gauss_beam(KTP, wl, waist, pol=pol),
]
xmin_bc = dict(TE="PEC", TM="PMC")
ymin_bc = dict(TE="PMC", TM="PEC")
sim.mesh.set_boundary("xmin", xmin_bc[pol])
sim.mesh.set_boundary("ymin", ymin_bc[pol])
sim.mesh.box = sim.mesh.box.modify(zmax=100)
pade_order = 0
smooth = 3
sol = sim.calc(wl, launch_field, smooth=smooth, pade_order=pade_order)
norm = np.max(np.abs(sol.e0))
z = sim.mesh.z[-1]
e_in = sol.e0.copy()
e_in_norm = np.linalg.norm(e_in) ** 2

# %% 
def monitor(sol):
    if "correlation" not in sol.monitor:
        sol.monitor["correlation"] = np.array([], dtype=np.complex128)
    if "power" not in sol.monitor:
        sol.monitor["power"] = np.array([], dtype=np.double)
    correlation = e_in.conj().dot(sol.e) / e_in_norm
    power = np.linalg.norm(sol.e) ** 2 / e_in_norm
    sol.monitor["correlation"] = np.r_[sol.monitor["correlation"], correlation]
    sol.monitor["power"] = np.r_[sol.monitor["power"], power]
    return correlation

def init():
    pass

def plot(sol, ax, norm, pcolormesh_kw=dict(), contour_kw=dict()):
    f = sol.ex if pol == "TE" else sol.ey
    data = 10 * np.log10(np.abs(f) / norm)
    im = ax[0].pcolormesh(sol.xcb.real, sol.y.real, data.T, **pcolormesh_kw)
    cont = ax[0].contour(sol.xcb.real, sol.y.real, data.T, **contour_kw)
    if pol == "TE":
        title = "$E_x$"
    else:
        title = "$E_y$"
    ax[0].set_title(title)
    ax[0].set_xlabel("x [um]")
    ax[0].set_ylabel("y [um]")
    if "correlation" in sol.monitor:
        power = sol.monitor["power"]
        P = sol.monitor["correlation"]
        z = np.arange(1, len(P) + 1) * dz
        fig.suptitle("z = {:.0f} um".format(z[-1]))
        ax[1].lines[0].set_data(z, 10 * np.log10(power))
        ax[2].lines[0].set_data(z, P.real)
        ax[2].lines[1].set_data(z, P.imag)
        zeta = np.fft.fftshift(np.fft.fftfreq(len(P), dz) / sol.k0)
        spectrum = np.fft.fftshift(np.fft.fft(P))
        ax[3].lines[0].set_data(zeta, np.abs(spectrum))
        for ax_ in ax[1:]:
            ax_.relim()
            ax_.autoscale_view()
    return *ax[1].lines, *ax[2].lines, *ax[3].lines


def update(frame):
    global z
    sim.calc(wl, sol, smooth=smooth, pade_order=pade_order, monitor=monitor)
    ax[0].clear()
    artists = plot(sol, ax, norm, pc_kw, cont_kw)
    return artists


fig = plt.figure(figsize=(10, 6), dpi=100)
gs = plt.GridSpec(3, 2, hspace=0.7, wspace=0.3)
ax = []
ax.append(fig.add_subplot(gs[:, 0]))
ax.append(fig.add_subplot(gs[0, 1]))
ax.append(fig.add_subplot(gs[1, 1]))
ax.append(fig.add_subplot(gs[2, 1]))
dummy_data = [[], []]
for ax_ in ax[1:]:
    ax_.plot(*dummy_data)
ax[2].plot(*dummy_data)
for ax_ in ax[1:3]:
    ax_.set_xlabel("z [um]")
ax[1].set_title("Relative Power")
ax[1].set_ylabel("[dB]")
ax[2].set_title(r"$\langle E(0)|E(z)\rangle$")
ax[3].set_title(r"$\langle E(0)|E(z)\rangle$ spectrum")
ax[3].set_yscale("log")
ax[3].set_xlabel("$\zeta$ [um${}^{-1}$]")
pc_kw = dict(cmap="jet", vmax=0, vmin=-20)
log_levels = [-20, -10, -10 * np.log10(np.e), -3]
cont_kw = dict(levels=log_levels, cmap='viridis')
plot(sol, ax, norm, pc_kw, cont_kw)
animation = FuncAnimation(fig, update, frames=1000, init_func=init, repeat=False)
plt.show()
    # %%
# animation.save("../data/bpm.gif")
