# cython: boundscheck=False, wraparound=False, cdivision=True
import numpy as np
cimport numpy as cnp

cnp.import_array()
DTYPE = np.float64
ctypedef cnp.float64_t DTYPE_t


def mcoe2(long n):
    cdef cnp.ndarray[DTYPE_t, ndim=2] res = np.zeros((n, n), dtype=DTYPE)
    cdef double[:,:] resv = res
    cdef Py_ssize_t i

    for i in range(1, n):
        resv[i, i - 1] = 1.
        resv[i, i] = 1.

    return res


def mcoe3(long n, cnp.ndarray[double, ndim=1] dx):
    cdef:
        cnp.ndarray[DTYPE_t, ndim=2] res = np.zeros((n, n), dtype=DTYPE)
        double[:,:] resv = res
        double[:] dxv = dx
        Py_ssize_t i

    for i in range(1, n - 1):
        resv[i, i - 1] = dxv[i - 1]
        resv[i, i] = 2. * (dxv[i] + dxv[i - 1])
        resv[i, i + 1] = dxv[i]

    return res
