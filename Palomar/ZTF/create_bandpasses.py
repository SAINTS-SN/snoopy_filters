#!/usr/bin/env python

from scipy.interpolate import splrep, splev
from scipy.signal import convolve
from scipy.signal.windows import boxcar
from numpy import loadtxt, savetxt, array
from pandas import read_csv
import numpy as np

# original filter functions from the ZTF github
g = read_csv("ZTF_g_band_test_data_pos1_0AOI.csv", header=None, names=["wl", "trans"])
r = read_csv("ZTF_r_band_test_data_pos1_0AOI.csv", header=None, names=["wl", "trans"])
i = read_csv("ztf_i_band.csv", header=None, names=["wl", "trans"])
i = i.reindex(index=i.index[::-1])

# QE
single = read_csv("e2v_ztf_singlelayer.csv", header=None, names=["wl", "trans"])
multi = read_csv("e2v_ztf_multi2.csv", header=None, names=["wl", "trans"])

# Atmosphere extinction
atm = read_csv("atm_ext_ctio.dat", header=None, names=["wl", "trans"], delimiter="\s+")
lines = read_csv(
    "atm_ext_lines.dat", header=None, names=["wl", "trans"], delimiter="\s+"
)

# First, down-sample the ztf filters with boxcar average
window = boxcar(10)
window = window / sum(window)  # normalize

wg = g["wl"][::10] * 10
rg = convolve(g["trans"], window, mode="same")[::10]
wr = r["wl"][::10] * 10
rr = convolve(r["trans"], window, mode="same")[::10]
wi = i["wl"][::10] * 10
ri = convolve(i["trans"], window, mode="same")[::10]

# We need to interpolate over atmospheric functions
tck_atm = splrep(atm["wl"], atm["trans"], k=3)  # Smooth function
tck_lines = splrep(lines["wl"], lines["trans"], k=1, s=0)  # less smooth

# We need to interpolate over QE functions
tck_single = splrep(single["wl"] * 10, single["trans"], k=3)
tck_multi = splrep(multi["wl"] * 10, multi["trans"], k=3)

# g-band only needs atm, no lines
rg = rg * splev(wg, tck_atm)
# r and i bands need the lines
rr = rr * splev(wr, tck_atm) * splev(wr, tck_lines)
ri = ri * splev(wi, tck_atm) * splev(wi, tck_lines)

for bp, w, r in zip("gri", (wg, wr, wi), (rg, rr, ri)):
    savetxt(
        f"{bp}_single.dat",
        array([w, r * splev(w, tck_single)]).T,
        # array([w, r * np.interp(w, single["wl"], single["trans"])]).T,
        fmt="%.8f",
    )
    savetxt(
        f"{bp}_multi.dat",
        array([w, r * splev(w, tck_multi)]).T,
        # array([w, r * np.interp(w, multi["wl"], multi["trans"])]).T,
        fmt="%.8f",
    )
    savetxt(
        f"{bp}_average.dat",
        array([w, r * (splev(w, tck_single) + splev(w, tck_multi)) / 2]).T,
        fmt="%.8f",
    )
