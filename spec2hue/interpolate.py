# -*- coding: utf-8 -*-

from numpy import argsort, asarray, c_, diff, insert, ndarray, zeros
from numpy.linalg import inv
try:
    from . import interp1d_coe
    INTERP1D_COE = True
except:
    INTERP1D_COE = False


def ndim_check(x: ndarray) -> ndarray:
    # 将二维向量转一维 其他不变 vector
    if x.ndim == 2 and 1 in x.shape:
        return x.ravel()
    return x


class interp1d:
    kind_str = ('linear', 'quadratic', 'cubic')
    boundary_str = ('natural', 'not-a-knot', 'periodic')

    def __init__(self, x: ndarray, y: ndarray, axis=0, kind=3, boundary='not-a-knot'):
        self.input_check(x, y, axis, kind, boundary.lower())

        if self.kind == 1:
            fun = self.mcoe_cal1
        elif self.kind == 3:
            fun = self.mcoe_cal3
        elif self.kind == 2:
            fun = self.mcoe_cal2
        if self.y.ndim == 1:
            self.mcoe = fun(self.y)
        else:
            self.mcoe = [fun(ii) for ii in self.y]

    def input_check(self, x, y, axis, kind, boundary):
        x, y = asarray(x), asarray(y)
        # x 一维向量
        if x.ndim != 1 and (x.shape[0] - 1) * (x.shape[1] - 1) != 0:
            raise ValueError('x is not vector')
        x = ndim_check(x)
        x_sort_index = argsort(x)
        self.x = x[x_sort_index]

        # y 一维向量 | 二维行向量的堆叠
        if y.ndim != 1:
            y = ndim_check(y)
            if y.ndim == 2:
                if axis == 0:  # 对列内
                    self.y = y[x_sort_index].T
                elif axis == 1:  # 对行内
                    self.y = y[:, x_sort_index]
                else:
                    raise ValueError('axis must in (0, 1)')
        if y.ndim == 1:
            if y.size != x.size:
                raise ValueError('y.size != x.size')
            self.y = y[x_sort_index]
        elif y.ndim > 2:
            raise ValueError('y.ndim > 2')

        # kind
        if isinstance(kind, int):
            if kind in (1, 2, 3):
                self.kind = kind
            else:
                raise ValueError('kind must in (1, 2, 3)')
        elif isinstance(kind, str):
            kind = kind.lower()
            if kind in self.kind_str:
                self.kind = self.kind_str.index(kind) + 1
            else:
                raise ValueError('kind must in ("linear", "quadratic", "cubic")')
        else:
            raise ValueError('kind must in (int, str)')

        # boundary
        if boundary in self.boundary_str:
            self.boundary = self.boundary_str.index(boundary)
        else:
            raise ValueError('boundary must in ("natural", "periodic", "not-a-knot")')

    def xin_index(self, x_in: ndarray):
        xin_ind, start = [], 0
        for i1 in x_in:
            if i1 >= self.x[-1]:
                xin_ind.append(self.x.size - 2)
                continue
            for i2 in range(start, self.x.size - 1):
                if i1 < self.x[i2 + 1]:
                    xin_ind.append(i2)
                    start = i2
                    break
        return xin_ind

    def __call__(self, x_in: ndarray) -> ndarray:
        x_in = asarray(x_in).flatten()
        x_in.sort()
        x_in_ind = self.xin_index(x_in)
        # c_[tuple([x_in**ii for ii in range(self.kind + 1)])]
        X = x_in[:, None]**range(self.kind + 1)

        if self.y.ndim == 1:
            res = [self.mcoe[val] @ X[ii] for ii, val in enumerate(x_in_ind)]
            return asarray(res)
        else:
            res = [[coe[val] @ X[ii] for ii, val in enumerate(x_in_ind)]
                   for coe in self.mcoe]
            return c_[tuple(res)]

    def mcoe_cal1(self, y) -> ndarray:
        dx, dy = diff(self.x), diff(y)
        k = dy / dx
        a, xx = y[:-1], self.x[:-1]
        return c_[a - k * xx, k]

    def mcoe_cal2(self, y) -> ndarray:
        dx, dy = diff(self.x), diff(y)
        # k = dy/dx
        a, xx = y[:-1], self.x[:-1]
        # yy = 2 * dy / dx
        yy = insert(2 * dy / dx, 0, 0)

        if INTERP1D_COE:
            mcoe = interp1d_coe.mcoe2(self.x.size)
        else:
            mcoe = zeros([self.x.size, self.x.size])
            for ii in range(1, self.x.size):
                mcoe[ii, ii - 1] = 1
                mcoe[ii, ii] = 1

        if self.boundary == 0:
            mcoe[0, 0] = 1
        elif self.boundary == 1:
            mcoe[0, 0] = dx[1]
            mcoe[0, 1] = -(dx[0] + dx[1])
            mcoe[0, 2] = dx[0]
        elif self.boundary == 2:
            mcoe[0, 0] = 1
            mcoe[0, -1] = -1

        b_ = inv(mcoe) @ yy
        b = b_[:-1]
        c = diff(b_) / dx / 2
        return c_[a - b * xx + c * xx**2, b - c * xx * 2, c]

    def mcoe_cal3(self, y) -> ndarray:
        dx, dy = diff(self.x), diff(y)
        k = dy / dx
        a, xx = y[:-1], self.x[:-1]

        yy = diff(k) * 3
        yy = insert(yy, [0, yy.size], 0)
        if INTERP1D_COE:
            mcoe = interp1d_coe.mcoe3(self.x.size, asarray(dx, float))
        else:
            mcoe = zeros([self.x.size, self.x.size])
            for ii in range(1, self.x.size - 1):
                mcoe[ii, ii - 1] = dx[ii - 1]
                mcoe[ii, ii] = 2 * (dx[ii] + dx[ii - 1])
                mcoe[ii, ii + 1] = dx[ii]

        if self.boundary == 0:
            mcoe[0, 0], mcoe[-1, -1] = 1, 1
        elif self.boundary == 1:
            mcoe[0, 0] = -dx[1]
            mcoe[0, 1] = dx[0] + dx[1]
            mcoe[0, 2] = -dx[0]
            mcoe[-1, -1] = -dx[-2]
            mcoe[-1, -2] = dx[-1] + dx[-2]
            mcoe[-1, -3] = -dx[-1]
        elif self.boundary == 2:
            mcoe[0, 0] = 1
            mcoe[0, -1] = -1
            mcoe[-1, -1] = dx[-1] / 6
            mcoe[-1, -2] = dx[-1] / 3
            mcoe[-1, 1] = -dx[0] / 6
            mcoe[-1, 0] = -dx[0] / 3
            yy[-1] = dy[-1] - dy[0]

        c0 = inv(mcoe) @ yy
        c = c0[:-1]
        d = diff(c0) / dx / 3
        b = k - dx * c * 2 / 3 - dx * c0[1:] / 3
        return c_[a - b * xx + c * xx**2 - d * xx**3,
                  b - c * xx * 2 + d * xx**2 * 3, c - d * xx * 3, d]
