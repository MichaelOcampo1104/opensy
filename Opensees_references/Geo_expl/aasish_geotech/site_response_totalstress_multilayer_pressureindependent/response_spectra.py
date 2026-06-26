#!/usr/bin/env python
# -*-coding:utf-8 -*-

import numpy as np
import pandas as pd

# from scipy import integrate
from pathlib import Path
import matplotlib.pyplot as plt
from itertools import product
import eqsig.single as eq

# Font settings
plt.rc("font", **{"family": "sans-serif", "sans-serif": ["DejaVu Sans"]})
# plt.rc('font', **{'family': 'serif', 'serif': ['Times New Roman']})
params = {
    "axes.labelsize": 12,
    "font.size": 12,
    "legend.fontsize": 12,
    "xtick.labelsize": 12,
    "ytick.labelsize": 12,
    # use Tex to render all fonts
    "text.usetex": True,
    "axes.unicode_minus": True,
}
plt.rcParams.update(params)

# Close all open figures
plt.close("all")


# Description: Compute spectral displacements of SDOF subjected to base excitation
# where the base excitation is the surface ground acceleration. Write those values to
# output file for later plotting.
# the transfer function of the ratio of displacement of the SDOF to ground acceleration
# is based on the equation given in Geotechnical Earthquake Engineering by Steven L. Kramer
# pg 57 Eq 3.3, then compute pseudo velocity spectrum and displacement spectrum
# One can also derive the equations as given in
# ref: http://people.duke.edu/~hpgavin/cee201/sdof-dyn.pdf
# Also spectral values are determined using Nigam and Jennings (1969)
# ref: https://pdfs.semanticscholar.org/abb0/466b871bdb94b3ac61136926aa63d7d556bc.pdf


def get_nodalvalues(fpath, ndof, nodetag):
    """Get the data from output file for the given node
    fpath: full path including the filename of the output file
    ndof: number of variables or dofs reported at each node
    nodetag: the node number at which data is desired
    return 1d arrays of timestep and the requested variable
    """

    # read acceleration data
    # How is the data arranged? the first column is dt
    # Then the following columns are accelrations for
    # node1_dof1, node1_dof2, node2_dof1, node2_dof2 and so on
    # for the number of nodes
    data = np.loadtxt(fpath)

    # first create the timestep column from the data
    # dts = data[:, 0]
    # all the columns except the first timestep column
    data = data[:, 1:]

    # transposing makes it easy to manipulate data
    data = data.T
    # Check if it is really the timestep column,
    # comment this line if not needed
    # print(
    # f"Shape of the time steps: {dts.shape}, Average dt: {np.mean(np.diff(dts))} s"
    # )

    # number of rows (number of timesteps) and columns (number of nodes x ndf)
    nr, nc = data.shape
    print(f"Shape of acceleration vector: {nr} {nc}")

    # reshape 2D array data into 3D array data, where the depth frames are the different nodes
    # two nodes and two dofs per node (4 columns) and three time steps (number of rows)
    # e.g if a = [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10, 11]]
    # for easier grouping using transpose b = a.T => [[ 0  4  8], [ 1  5  9], [ 2  6 10], [ 3  7 11]]
    # reshape d = np.reshape(b, (2, 2, 3)) where (nf, nc, nr) nf = number of frames
    # nc = number of columns, nr is the number of rows =>
    # [[[ 0  4  8]
    #    [ 1  5  9]]
    #
    # [[ 2  6 10]
    #    [ 3  7 11]]]
    # so in the above, assume the data for two nodes with ndf=2 and three timesteps so we want
    # to group [[0, 1], [4, 5], [8, 9]] in the first frame for node1
    # and [[2, 3], [6, 7], [10, 11]] in the second frame for node2
    # each row contains values for different time step for ndf
    # due to transpose the values are rowwise instead of column wise
    # so instead of [[0, 1], [4, 5], [8, 9]] in the first frame for node1 we get
    # [[0, 4, 8], [1, 5, 9]] due to transpose.
    # after removing the time step column the first column,
    # the number of columns = number of nodes * ndofs (or the number variables reported per node)
    nnodes = int(nr / ndof)
    print(f"Number of nodes: {nnodes}")
    data = np.reshape(data, (nnodes, ndof, nc))
    fr, nr, nc = data.shape
    print(
        f"Shape of acceleration vector: Frame (nodes): {fr}, Rows (dofs): {nr}, Columns (timesteps): {nc}"
    )

    # 0 array indexing, therefore where nodetag is n then index is n - 1
    # 3D data [frames, row, column]
    # frames = nodes
    # and due to Transpose
    # row = dofs 0: dof = 1, and 1: dof = 2
    # column: timesteps
    return data[nodetag - 1, 0, :]


def nigjen_acoeffs(xi, omega, dt):
    """Compute the A matrix for SDOF response from Nigam and Jennings (1969) paper
    xi: critical damping xi = c/cc where cc = 2 * sqrt(km)
    omega: angular natural frequency of the SDOF structure
    dt: time step between two acceleration records
    ref:Nigam, N. C., and Jennings, P. C. (1969). CALCULATION OF RESPONSE SPECTRA FROM STRONG-5~OTION EARTHQUAKE RECORDS
    Bulletin of the Seismological Society of America. Vol. 59, No. 2, pp. 909-922. April, 1969
    """
    expterm = np.exp(-xi * omega * dt)
    omegad = omega * np.sqrt(1 - xi ** 2)
    sine = np.sin(omegad * dt)
    cosine = np.cos(omegad * dt)

    a11 = expterm * (omega / omegad * xi * sine + cosine)

    a12 = expterm / omegad * sine

    a21 = -omega ** 2 / omegad * expterm * sine

    a22 = expterm * (cosine - omega / omegad * xi * sine)
    # print(a11, a12, a21, a22)

    return np.array([[a11, a12], [a21, a22]])


def nigjen_bcoeffs(xi, omega, dt):
    """Compute the B matrix for SDOF response from Nigam and Jennings (1968) paper
    xi: critical damping xi = c/cc where cc = 2 * sqrt(km)
    omega: angular natural frequency of the SDOF structure
    dt: time step between two acceleration records 
    """
    expterm = np.exp(-xi * omega * dt)
    damp = np.sqrt(1 - xi ** 2)
    omegad = omega * np.sqrt(1 - xi ** 2)
    sine = np.sin(omegad * dt)
    cosine = np.cos(omegad * dt)

    b11 = expterm * (
        ((2 * xi ** 2 - 1) / (omega ** 2 * dt) + xi / omega) * sine / omegad
        + (2 * xi / (omega ** 3 * dt) + 1 / omega ** 2) * cosine
    ) - 2 * xi / (omega ** 3 * dt)

    b12 = (
        -expterm
        * (
            (2 * xi ** 2 - 1) / (omega ** 2 * dt) * sine / omegad
            + 2 * xi / (omega ** 3 * dt) * cosine
        )
        - 1 / omega ** 2
        + 2 * xi / (omega ** 3 * dt)
    )

    b21 = expterm * (
        ((2 * xi ** 2 - 1) / (omega ** 2 * dt) + xi / omega)
        * (cosine - omega / omegad * xi * sine)
        - (2 * xi / (omega ** 3 * dt) + 1 / omega ** 2)
        * (omegad * sine + xi * omega * cosine)
    ) + 1 / (omega ** 2 * dt)

    b22 = -expterm * (
        (2 * xi ** 2 - 1) / (omega ** 2 * dt) * (cosine - omega / omegad * xi * sine)
        - 2 * xi / (omega ** 3 * dt) * (omegad * sine + xi * omega * cosine)
    ) - 1 / (omega ** 2 * dt)

    return np.array([[b11, b12], [b21, b22]])


def compute_a_and_b(xi, w, dt):
    """
    From the paper by Nigam and Jennings (1968), computes the two matrices.
    :param xi: critical damping ratio
    :param w: angular frequencies
    :param dt: time step
    :return: matrices A and B
    """
    # ref: https://github.com/eng-tools/eqsig/blob/master/eqsig/sdof.py
    # I used this from EQSIG module to check my A and B matrices

    # Reduce the terms since all is matrix multiplication.
    xi2 = xi * xi  # D2
    w2 = w ** 2  # W2
    one_ov_w2 = 1.0 / w2  # A7
    sqrt_b2 = np.sqrt(1.0 - xi2)
    w_sqrt_b2 = w * sqrt_b2  # A1

    exp_b = np.exp(-xi * w * dt)  # A0
    two_b_ov_w2 = (2 * xi ** 2 - 1) / (w ** 2 * dt)
    two_b_ov_w3 = 2 * xi / (w ** 3 * dt)

    sin_wsqrt = np.sin(w_sqrt_b2 * dt)  # A2
    cos_wsqrt = np.cos(w_sqrt_b2 * dt)  # A3

    # A matrix
    a_11 = exp_b * (xi / sqrt_b2 * sin_wsqrt + cos_wsqrt)  # Eq 2.7d(1)
    a_12 = exp_b / (w * sqrt_b2) * sin_wsqrt  # Eq 2.7d(2)
    a_21 = -w / sqrt_b2 * exp_b * sin_wsqrt  # Eq 2.7d(3)
    a_22 = exp_b * (cos_wsqrt - xi / sqrt_b2 * sin_wsqrt)  # Eq 2.7d(4)

    a = np.array([[a_11, a_12], [a_21, a_22]])

    # B matrix
    bsqrd_ov_w2_p_xi_ov_w = two_b_ov_w2 + xi / w
    sin_ov_wsqrt = sin_wsqrt / w_sqrt_b2
    xwcos = xi * w * cos_wsqrt
    wsqrtsin = w_sqrt_b2 * sin_wsqrt

    # Eq 2.7e
    b_11 = (
        exp_b
        * (bsqrd_ov_w2_p_xi_ov_w * sin_ov_wsqrt + (two_b_ov_w3 + one_ov_w2) * cos_wsqrt)
        - two_b_ov_w3
    )
    b_12 = (
        -exp_b * (two_b_ov_w2 * sin_ov_wsqrt + two_b_ov_w3 * cos_wsqrt)
        - one_ov_w2
        + two_b_ov_w3
    )
    b_21 = (
        exp_b
        * (
            bsqrd_ov_w2_p_xi_ov_w * (cos_wsqrt - xi / sqrt_b2 * sin_wsqrt)
            - (two_b_ov_w3 + one_ov_w2) * (wsqrtsin + xwcos)
        )
        + one_ov_w2 / dt
    )
    b_22 = (
        -exp_b
        * (
            two_b_ov_w2 * (cos_wsqrt - xi / sqrt_b2 * sin_wsqrt)
            - two_b_ov_w3 * (wsqrtsin + xwcos)
        )
        - one_ov_w2 / dt
    )

    b = np.array([[b_11, b_12], [b_21, b_22]])

    return a, b


def nigam_and_jennings_response(acc, dt, periods, xi):
    """
    Implementation of the response spectrum calculation from Nigam and Jennings (1968).
    Ref: Nigam, N. C., Jennings, P. C. (1968) Digital calculation of response spectra from strong-motion earthquake
    records. National Science Foundation.
    :param acc: acceleration in m/s2
    :param periods: response periods of interest
    :param dt: time step of the acceleration time series
    :param xi: critical damping factor
    :return: response displacement, response velocity, response acceleration
    """
    # ref: https://github.com/eng-tools/eqsig/blob/master/eqsig/sdof.py
    # I used this function from the EQSIG module to check my code for the response of SDOF

    acc = -np.array(acc).astype(np.float)
    periods = np.array(periods).astype(np.float)
    w = 6.2831853 / periods
    dt = np.float(dt)
    xi = np.float(xi)

    # implement: delta_t should be less than period / 20
    a, b = compute_a_and_b(xi, w, dt)

    resp_u = np.zeros([len(w), len(acc)], dtype=np.float)
    resp_v = np.zeros([len(w), len(acc)], dtype=np.float)

    for i in range(len(acc) - 1):  # possibly speed up using scipy.signal.lfilter
        # x_i+1 = A cross (u, v) + B cross (acc_i, acc_i+1)  # Eq 2.7a
        resp_u[:, i + 1] = (
            a[0][0] * resp_u[:, i]
            + a[0][1] * resp_v[:, i]
            + b[0][0] * acc[i]
            + b[0][1] * acc[i + 1]
        )
        resp_v[:, i + 1] = (
            a[1][0] * resp_u[:, i]
            + a[1][1] * resp_v[:, i]
            + b[1][0] * acc[i]
            + b[1][1] * acc[i + 1]
        )

    w2 = w ** 2
    sdof_acc = -2 * xi * w[:, np.newaxis] * resp_v - w2[:, np.newaxis] * resp_u

    return resp_u, resp_v, sdof_acc


def nigam_jennings_integration(x, a, dt, xi, omega):
    """Integration proposed by Nigam and Jennings (1968) to compute response of SDOF
    x: array of [xi, vi]
    a: array of [ai, ai+1]
    xi:  damping ratio
    omega: natural frequency of the SDOF
    dt: time interval between two data points
    """
    mat_a = nigjen_acoeffs(xi, omega, dt)
    mat_b = nigjen_bcoeffs(xi, omega, dt)
    # mat_a = np.array([[1, 1], [1, 1]])
    # mat_b = np.array([[2, 2], [2, 2]])
    # matrix multiplication, can be done in a variety of ways in numpy b: 2 x 2 time x: 2 x 1 = c: 2 x 1
    # this is how it is internally arranged even when x is 1d array which is 1 x 2 in our case
    # c = np.matmul(mat_a, x) + np.matmul(mat_b, a)
    # print(f"A: {mat_a}, B: {mat_b}, c: {c}")
    return np.matmul(mat_a, x) + np.matmul(mat_b, a)


def nigam_jennings_constant_dt_integration(x, a, mat_a, mat_b):
    """Integration proposed by Nigam and Jennings (1968) to compute response of SDOF
    x: array of [xi, vi]
    a: array of [ai, ai+1]
    mat_a: 2 x 2 matrix of coefficients A
    mat_b: 2 x 2 matrix of coefficients B
    """

    # matrix multiplication, can be done in a variety of ways in numpy b: 2 x 2 time x: 2 x 1 = c: 2 x 1
    # this is how it is internally arranged even when x is 1d array which is 1 x 2 in our case
    # c = np.matmul(mat_a, x) + np.matmul(mat_b, a)
    # print(f"A: {mat_a}, B: {mat_b}, c: {c}")
    return np.matmul(mat_a, x) + np.matmul(mat_b, a)


def sdof_relativeresponse_baseexcitation(gm, dt, xi, period):
    """Compute displacement, velocity and acceleration response spectra
    gm: digitized ground motions, accelerations, at fixed intervals
    dt: fixed interval of ground motion record
    xi: damping ratio xi = c/cc where cc is cricital damping
    omega: natural period of the SDOF
    """
    # create temporary variables to store intermediate steps
    # gm = -np.concatenate(([0], gm))
    gm = -gm
    nsteps = len(gm)

    # convert from time period to angular frequency
    omega = 2 * np.pi / period

    # assumes that this is the complete record and x0 and v0 are zeros
    x = np.zeros([2, nsteps], dtype=np.float)

    a = nigjen_acoeffs(xi, omega, dt)
    b = nigjen_bcoeffs(xi, omega, dt)
    # print(f"A: {mat_a}, B: {mat_b}")

    # compute relative displacements and velocities of SDOF lumped mass to base excitation
    for i in range(nsteps - 1):
        x[:, i + 1] = nigam_jennings_constant_dt_integration(
            x[:, i], gm[i : i + 2], a, b
        )
        # x[0, i + 1] = a[0][0] * x[0, i] + a[1][0] * x[1, i] + b[0][0] * gm[i] + b[0][1] * gm[i+1]
        # x[1, i + 1] = a[1][0] * x[0, i] + a[1][1] * x[1, i] + b[1][0] * gm[i] + b[1][1] * gm[i + 1]

    # compute acceleration from the velocities and displacements
    z = -(2 * xi * omega * x[1] + omega ** 2 * x[0])

    # save and return spectral displacement, velocity and acceleration
    umax = np.max(np.abs(x[0]))
    vmax = np.max(np.abs(x[1]))
    amax = np.max(np.abs(z))

    return [umax, vmax, amax]


def response_spectrum_frequency(gm, dt, xi, periods):
    """Compute spectral displacement using frequency domain equations
    then compute pseudo spectral velocity and acceleration 
    gm: digitized ground motions, accelerations, at fixed intervals
    dt: fixed interval of ground motion record
    xi: damping ratio xi = c/cc where cc is cricital damping
    period: natural periods of the SDOF
    """

    # sample length
    n = gm.size

    # convert from oscillation periods to angular frequency
    omegans = 2 * np.pi / periods

    # DFFT amplitudes and frequencies, frequency is Hz
    rfftamps = np.fft.rfft(gm)
    freqs = np.fft.rfftfreq(n, d=dt)

    # change frequency to circular frequency rad/s
    omegas = 2 * np.pi * freqs

    # for saving the spectral values in the a file
    odata = np.zeros((len(omegans), 4), dtype=np.float)

    # working in frequency domain with transfer function for each omegan
    for idx, omegan in enumerate(omegans):
        fratios = omegas / omegan
        trnsfcn = 1 / (omegan ** 2 * ((1 - fratios ** 2) + (2j * xi * fratios)))

        # displacement in frequency domain
        u = rfftamps * trnsfcn

        # change to time domain displacement
        ut = np.fft.irfft(u)

        # maximum reponse
        utmax = np.max(np.abs(ut))

        # convert the circular frequencies to time periods,
        # find the maximum response, displacement, pseudo velocity and acceleration
        odata[idx, 0] = 2 * np.pi / omegan
        odata[idx, 1] = utmax
        odata[idx, 2] = omegan * utmax
        odata[idx, 3] = omegan ** 2 * utmax

    return odata


def main():
    # paths and filenames
    path_root = Path(r"./")
    path_data = path_root / "data"

    # filenames and paths
    fname_acc = "ex_g_02_siteresponse_multilayer_pressureindependent_totalstress_accel.out"
    fname_nijen = "ex_g_02_response_spectra_nijen_damp0p05.csv"
    fname_freq = "ex_g_02_reponse_spectra_freq_damp0p05.csv"
    fname_rec = "ex_g_02_reponse_spectra_eqsig_damp0p05.csv"
    f_acc = path_data.joinpath(fname_acc)
    f_nijen = path_data.joinpath(fname_nijen)
    f_freq = path_data.joinpath(fname_freq)
    f_rec = path_data.joinpath(fname_rec)

    # time step of data [s]
    dt = 0.005

    # accelaration due to gravity [m/s2]
    accg = 9.81

    # degrees of freedom in the analysis ndof
    ndofs = 2

    # node for output
    nodetag = 301

    # damping ratio
    dampratio = 0.05

    # range of natural frequencies for the SDOF
    nperiods = 100
    minpower = -3
    maxpower = 1
    periods = np.logspace(minpower, maxpower, nperiods)

    # ground motion data from a specified node
    gm = get_nodalvalues(f_acc, ndofs, nodetag)

    # spectral respone using Nigam Jennings method, this does not give the same reponse
    # as the frequency domain solution and the Nigam Jennings from EQSIG package, so needs fixing but
    # in the mean time can use the eqsig package
    spectral_data = []
    for period in periods:
        x = sdof_relativeresponse_baseexcitation(gm, dt, dampratio, period)
        spectral_data.append([period, *x])

    # change list to array for easy manipulation
    nigam_odata = np.asarray(spectral_data)
    nigam_odata[:, 3] = nigam_odata[:, 3] / accg

    # spectral reponse using in frequency domain using transfer function
    freq_odata = response_spectrum_frequency(gm, dt, dampratio, periods)
    freq_odata[:, 3] = freq_odata[:, 3] / accg

    # spectral response from EQSIG package
    record = eq.AccSignal(gm, dt)
    record.generate_response_spectrum(response_times=periods)
    eqrec = np.c_[
        periods[:, np.newaxis],
        record.s_d[:, np.newaxis],
        record.s_v[:, np.newaxis],
        record.s_a[:, np.newaxis] / accg,
    ]

    # create a pandas dataframe and then write the value to files
    colnames = ["Period [s]", "umax [m]", "vmax [m/s]", "amax [g]"]
    df_nijen = pd.DataFrame(data=nigam_odata, columns=colnames)
    df_freq = pd.DataFrame(data=freq_odata, columns=colnames)
    df_rec = pd.DataFrame(data=eqrec, columns=colnames)
    # df_nijen.to_csv(f_nijen, index=False)
    df_freq.to_csv(f_freq, index=False)
    df_rec.to_csv(f_rec, index=False)


if __name__ == "__main__":
    main()
    # cProfile.run('main()')

