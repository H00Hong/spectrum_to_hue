# -*- coding: utf-8 -*-
"""
CIE1931|1964|1976色度计算
"""
from typing import Literal, Tuple, Union

from cie_data import (Mrgb, Mrgb2, aKabHunter, aSIValue, aStandardIlluminant,
                      aWhitePoint, aWhitePointHunter, axyzL)
from interpolate import interp1d
from numpy import (arange, arctan2, asarray, c_, ceil, clip, diff, float64,
                   floor, nan_to_num, ndarray, pi, sqrt)
from numpy.typing import NDArray

# %% functions
_POW1, _POW2 = float64(1 / 3), float64(3)
_A1, _A2 = float64(216 / 24389), float64(6 / 29)
_B1, _B2, _B0 = float64(841 / 108), float64(108 / 841), float64(4 / 29)


def _ff(t):
    return t**_POW1 * (t > _A1) + (_B1 * t + _B0) * (t <= _A1)


def _ff_(t):
    return t**_POW2 * (t > _A2) + (t - _B0) * _B2 * (t <= _A2)


def _input_check(s) -> ndarray:
    s = asarray(s)
    if s.ndim not in (1, 2):
        raise ValueError(f"ndim must be 1 or 2, but got {s.ndim}")
    if s.ndim == 2 :
        if 1 in s.shape:
            return s.ravel()
        if s.shape[0] != 3:
            raise ValueError(f"shape[0] must be 3, but got {s.shape[0]}")
        return s
    return s


class CIEHueTransform:
    """
    CIE1931|1964|1976色度转换

    Parameters
    ----------
    SI : {'A','D65','C','D50','D55','D75'}
        光源  默认'D65'
    vi : {2, 10}
        视场角 默认2

    Methods
    -------
    - xyz2lab(XYZ):   CIE XYZ to CIE 1976(L*a*b*)colour space
    - xyz2lab_h(XYZ): CIE XYZ to HunterLab
    - xyz2yuv(XYZ):   CIE XYZ to CIE Yu'v'
    - xyz2yxy(XYZ):   CIE XYZ to CIE Yxy
    - xyz2luv(XYZ):   CIE XYZ to CIE 1976 (L*u*v*) colour space
    - xyz2rgb(XYZ):   CIE XYZ to sRGB
    - lab2xyz(Lab):   CIE 1976 (L*a*b*) colour space to CIE XYZ
    - lab_h2xyz(Lab): HunterLab to CIE XYZ
    - yuv2xyz(Yuv):   CIE Yu'v' to CIE XYZ
    - yxy2xyz(Yxy):   CIE Yxy to CIE XYZ
    - luv2xyz(Luv):   CIE 1976 (L*u*v*) colour space to CIE XYZ
    - rgb2xyz(sRGB):  sRGB to CIE XYZ
    - chs(Lab|Luv):   CIE 1976 (L*a*b*)|(L*u*v*) colour space to Chs
    - lab2rgb(Lab):   CIE 1976 (L*a*b*) colour space to sRGB
    - rgb2lab(sRGB):  sRGB to CIE 1976 (L*a*b*) colour space
    - rgb16(sRGB):    sRGB to 16-sRGB
    - rbg16_(16-sRGB): 16-sRGB to sRGB
    """

    _wp_t: Tuple[NDArray[float64], NDArray[float64]]
    _wp_h_t: Tuple[NDArray[float64], NDArray[float64]]
    __slots__ = ['si_v', 'vi_v', '_wp_t', '_wp_h_t', 'wp', 'wp_h', 'kab']

    def __init__(self,
                 si: Literal['A', 'D65', 'C', 'D50', 'D55', 'D75',
                             'a', 'd65', 'c', 'd50', 'd55', 'd75'] = 'D65',
                 vi: Literal[2, 10] = 2):
        si = si.upper()  # type: ignore
        if si in aSIValue:
            self.si_v = aSIValue.index(si)
        else:
            raise ValueError(f'{self.__class__}: 光源种类错误')
        if vi == 2:
            self.vi_v = 0
        elif vi == 10:
            self.vi_v = 1
        else:
            raise ValueError(f'{self.__class__}: 视场角错误')
        # 当前光源下的白点
        self.wp: NDArray[float64] = aWhitePoint[self.vi_v, :, self.si_v]
        self.wp_h: NDArray[float64] = aWhitePointHunter[self.vi_v, :,
                                                        self.si_v]
        self.kab: NDArray[float64] = aKabHunter[self.vi_v, :, self.si_v]

        self._wp_t = (self.wp, self.wp[:, None])
        self._wp_h_t = (self.wp_h, self.wp_h[:, None])

    def _xyz2lab(self, s: ndarray) -> NDArray[float64]:
        wp = self._wp_t[s.ndim - 1]
        x1, y1, z1 = _ff(s / wp)
        L = 116 * y1 - 16
        a = 500 * (x1 - y1)
        b = 200 * (y1 - z1)
        return asarray((L, a, b))

    def _xyz2lab_h(self, s: ndarray) -> NDArray[float64]:
        x1, y1, z1 = s / self._wp_h_t[s.ndim - 1]
        y2 = sqrt(y1)
        L = 100 * y2
        a = self.kab[0] * (x1 - y1) / y2
        b = self.kab[1] * (y1 - z1) / y2
        return asarray((L, a, b))

    def _xyz2yuv(self, s: ndarray) -> NDArray[float64]:
        x, y, z = s
        fm = x + 15 * y + 3 * z
        return asarray((y, 4 * x / fm, 9 * y / fm))

    def _xyz2yxy(self, s: ndarray) -> NDArray[float64]:
        temp = s[[0, 1]] / s.sum(axis=0)
        return asarray((s[1], *temp))

    def _xyz2luv(self, s: ndarray) -> NDArray[float64]:
        uv = self._xyz2yuv(s)[1:]
        uvn = self._xyz2yuv(self._wp_t[s.ndim - 1])[1:]
        L = _ff(s[1] / 100) * 116 - 16
        u, v = 13 * L * (uv - uvn)
        return asarray((L, u, v))

    def _xyz2rgb(self, s) -> NDArray[float64]:
        y1 = Mrgb @ s / 100
        y2 = 1.055 * (y1**(1 / 2.4) - 0.055)
        y2 = nan_to_num(y2)
        y3 = 12.92 * y1
        # http://www.brucelindbloom.com/index.html?WorkingSpaceInfo.html
        res = y2 * (y1 > 0.0031308) + y3 * (y1 <= 0.0031308)
        return clip(res, 0, 1)

    @staticmethod
    def chs(s: ndarray) -> NDArray[float64]:
        """get C, h, s from Lab or Luv"""
        # s = _input_check(s)
        L, u, v = s
        C = sqrt(u**2 + v**2)
        h = arctan2(v, u) * 180 / pi
        s = C / L
        return asarray((C, h, s))

    def _lab2xyz(self, s: ndarray) -> NDArray[float64]:
        L, a, b = s
        y1 = (L + 16) / 116
        x1 = a / 500 + y1
        z1 = y1 - b / 200
        return _ff_(asarray((x1, y1, z1))) * self._wp_t[s.ndim - 1]

    def _lab_h2xyz(self, s: ndarray) -> NDArray[float64]:
        L, a, b = s
        y0 = L**2 / 10000
        x0 = a / self.kab[0] * L / 100 + y0
        z0 = y0 - b / self.kab[1] * L / 100
        return asarray((x0, y0, z0)) * self._wp_h_t[s.ndim - 1]

    def _luv2xyz(self, s: ndarray) -> NDArray[float64]:
        uvn = self._xyz2yuv(self._wp_t[s.ndim - 1])[1:]
        L = s[0]
        u_, v_ = s[1:] / 13 / L + uvn
        Y = _ff_((L + 16) / 116) * 100
        X = 9 / 4 * u_ / v_ * Y
        Z = 3 * Y / v_ - X / 3 - 5 * Y
        return asarray((X, Y, Z))

    def _yxy2xyz(self, s: ndarray) -> NDArray[float64]:
        all_sum = s[0] / s[2]
        return asarray((s[1] * all_sum, s[0], (1 - s[1] - s[2]) * all_sum))

    def _yuv2xyz(self, s: ndarray) -> NDArray[float64]:
        # (y, 4 * x / fm, 9 * y / fm)
        y = s[0]
        fm = 9 * y / s[2]  # x + 15 * y + 3 * z
        x = s[1] * fm / 4
        return asarray((x, y, (fm - x - 15 * y) / 3))

    def _rgb2xyz(self, s: ndarray) -> NDArray[float64]:
        s = clip(s, 0, 1)
        y1 = s / 12.92
        y2 = ((s + 0.055) / 1.055)**2.4
        yy = y1 * (s <= 0.04045) + y2 * (s > 0.04045)
        return Mrgb2 @ yy * 100

    def xyz2lab(self, s) -> NDArray[float64]:
        """
        XYZ to CIELab
        ----------

        输入：
            s : XYZ矩阵 行为 XYZ 列为输入项
        ----------

        输出：
            Lab矩阵 (CIELab, 输入项)
        """
        return self._xyz2lab(_input_check(s))

    def lab2xyz(self, s) -> NDArray[float64]:
        """
        CIELab to XYZ
        ----------

        输入：
            s : Lab矩阵 行为 CIELab 列为输入项
        ----------

        输出：
            XYZ矩阵 (XYZ, 输入项)
        """
        return self._lab2xyz(_input_check(s))

    def xyz2lab_h(self, s) -> NDArray[float64]:
        """XYZ to HunterLab"""
        return self._xyz2lab_h(_input_check(s))

    def lab_h2xyz(self, s) -> NDArray[float64]:
        """HunterLab to XYZ"""
        return self._lab_h2xyz(_input_check(s))

    def xyz2yuv(self, s) -> NDArray[float64]:
        """XYZ to Yu'v'"""
        return self._xyz2yuv(_input_check(s))

    def yuv2xyz(self, s) -> NDArray[float64]:
        """Yu'v' to XYZ"""
        return self._yuv2xyz(_input_check(s))

    def xyz2luv(self, s) -> NDArray[float64]:
        """XYZ to CIELuv"""
        return self._xyz2luv(_input_check(s))

    def luv2xyz(self, s) -> NDArray[float64]:
        """CIELuv to XYZ"""
        return self._luv2xyz(_input_check(s))

    def xyz2yxy(self, s) -> NDArray[float64]:
        """XYZ to Yxy"""
        return self._xyz2yxy(_input_check(s))

    def yxy2xyz(self, s) -> NDArray[float64]:
        """Yxy to XYZ"""
        return self._yxy2xyz(_input_check(s))

    def xyz2rgb(self, s) -> NDArray[float64]:
        """
        XYZ to sRGB
        ----------

        输入:
            s : XYZ矩阵, 行为 XYZ, 列为输入项
        ----------

        输出：
            sRGB矩阵 (RGB, 输入项)
        """
        # assert np.all(s >= 0 & s <= 100)
        return self._xyz2rgb(s)

    def rgb2xyz(self, s: ndarray) -> NDArray[float64]:
        """sRGB to XYZ"""
        return self._rgb2xyz(_input_check(s))

    def lab2rgb(self, s: ndarray) -> NDArray[float64]:
        """CIELab to sRGB"""
        return self._xyz2rgb(self._lab2xyz(_input_check(s)))

    def rgb2lab(self, s: ndarray) -> NDArray[float64]:
        """sRGB to CIELab"""
        return self._xyz2lab(self._rgb2xyz(_input_check(s)))

    def rgb16(self, s: ndarray, upper = 255) -> ndarray:
        """RGB[int,int,int] 转 16进制"""
        if upper != 255:
            s = (s/upper*255).round()
        s = clip(s.astype(int), 0, 255)
        if s.ndim == 1 or s.shape[0] == 1:
            s = s.reshape([3, 1])
        s_ = []
        for ic in range(s.shape[1]):
            ss_ = '#'
            for ir in range(s.shape[0]):
                s0 = hex(s[ir, ic])[-2:].replace('x', '0')
                ss_ = ss_ + s0
            s_.append(ss_)
        return asarray(s_)

    def rgb16_(self, rgbtxt: Union[ndarray, list, str],
               upper = 255) -> NDArray[float64]:
        """输出[0,1]的RGB"""
        if isinstance(rgbtxt, str):
            rgbtxt = [rgbtxt]
        for ii, val in enumerate(rgbtxt):
            if val[0] != '#' or len(val) != 7:
                raise ValueError('sRGB格式错误, 请输入带#的16进制颜色码')
            rgb = asarray([
                int(val[1:3], 16),
                int(val[3:5], 16),
                int(val[5:7], 16)
            ], dtype=float)
            if ii == 0:
                rgblst = rgb
            else:
                rgblst = c_[rgblst, rgb]
        return rgblst / upper  # type: ignore


############################
############################
class CIE(CIEHueTransform):
    """
    CIE1931|1964|1976色度计算

    Parameters
    ----------
    data : ndarray, list, tuple
        光谱
    SI : {'D65', 'A', 'C', 'D50', 'D55', 'D75'}
        光源  默认'D65'
    vi : {2, 10}
        视场角 默认2

    Methods
    -------
    - spe2xyz(): spectrum to CIE XYZ
    - spe2yxy(): spectrum to CIE Yxy
    - spe2yuv(): spectrum to CIE Yuv
    - spe2lab(): spectrum to CIE 1976 (L*a*b*) colour space
    - spe2lab_h(): spectrum to HunterLab
    - spe2luv(): spectrum to CIE 1976 (L*u*v*) colour space
    - spe2rgb(): spectrum to sRGB
    - xyz2lab(XYZ):   CIE XYZ to CIE 1976(L*a*b*)colour space
    - xyz2lab_h(XYZ): CIE XYZ to HunterLab
    - xyz2yuv(XYZ):   CIE XYZ to CIE Yu'v'
    - xyz2yxy(XYZ):   CIE XYZ to CIE Yxy
    - xyz2luv(XYZ):   CIE XYZ to CIE 1976 (L*u*v*) colour space
    - xyz2rgb(XYZ):   CIE XYZ to sRGB
    - lab2xyz(Lab):   CIE 1976 (L*a*b*) colour space to CIE XYZ
    - lab_h2xyz(Lab): HunterLab to CIE XYZ
    - yuv2xyz(Yuv):   CIE Yu'v' to CIE XYZ
    - yxy2xyz(Yxy):   CIE Yxy to CIE XYZ
    - luv2xyz(Luv):   CIE 1976 (L*u*v*) colour space to CIE XYZ
    - rgb2xyz(sRGB):  sRGB to CIE XYZ
    - chs(Lab|Luv):   CIE 1976 (L*a*b*)|(L*u*v*) colour space to Chs
    - lab2rgb(Lab):   CIE 1976 (L*a*b*) colour space to sRGB
    - rgb2lab(sRGB):  sRGB to CIE 1976 (L*a*b*) colour space
    - rgb16(sRGB):    sRGB to 16-sRGB
    - rbg16_(16-sRGB): 16-sRGB to sRGB
    """

    __slots__ = ['data', 'si0', 'xyzl0', 'sxyzl', 'spec_interp']

    def __init__(self, data: Union[ndarray, list, tuple],
                 si: Literal['A', 'D65', 'C', 'D50', 'D55', 'D75'] = 'D65',
                 vi: Literal[2, 10] = 2):
        super().__init__(si=si, vi=vi)
        if isinstance(data, (ndarray, list, tuple)):
            data = asarray(data)
            data = data[data[:, 0].argsort()]
            w = data[:, 0]
            data = data[:, 1:]
        else:
            raise ValueError(f'{self.__class__}: data格式错误')

        if w.max() < 3:
            w = w * 1000
        wn = w.min()
        wm = w.max()
        self.spec_interp = interp1d(w, data, axis=0, kind=3)

        dy = diff(w)
        if all(dy == dy[0]):
            step = int(clip(dy[0], 1, 10))
        else:
            dy_mean = dy.mean().round()
            step = int(clip(dy_mean, 1, 10))
        if wn > 400:
            raise ValueError(f'{self.__class__}: 光谱最小波长不能大于400nm')
        wn = floor(wn / step) * step if wn > 380 else 380
        if wm < 700:
            raise ValueError(f'{self.__class__}: 光谱最大波长不能小于700nm')
        wm = ceil(wm / step) * step if wm < 780 else 780
        lam = arange(wn, wm+step, step, int)

        self.data: NDArray[float64] = self.spec_interp(lam)
        # 当前波长下的光源功率分布
        self.si0: NDArray[float64] = aStandardIlluminant[lam - 380][:, 1 +
                                                                    self.si_v]
        # 当前波长和光源下的色匹配函数
        self.xyzl0: NDArray[float64] = axyzL[self.vi_v][lam-380].T[1:]
        self.sxyzl = self.si0 * self.xyzl0

    def spe2xyz(self) -> NDArray[float64]:
        """
        spectrum to XYZ
        ----------

        输出：
            XYZ矩阵 (XYZ, 输入项)
        """
        # sumXYZ = self.sxyzl@t/100
        # k = 100/np.sum(sxyz[1])
        return self.sxyzl @ self.data / self.sxyzl[1].sum()

    def spe2yxy(self) -> NDArray[float64]:
        """spectrum to Yxy"""
        return self._xyz2yxy(self.spe2xyz())

    def spe2yuv(self) -> NDArray[float64]:
        """spectrum to Yuv"""
        return self._xyz2yuv(self.spe2xyz())

    def spe2lab(self) -> NDArray[float64]:
        """spectrum to CIELAB"""
        return self._xyz2lab(self.spe2xyz())

    def spe2lab_h(self) -> NDArray[float64]:
        """spectrum to HunterLAB"""
        return self._xyz2lab_h(self.spe2xyz())

    def spe2luv(self) -> NDArray[float64]:
        """spectrum to CIELUV"""
        return self._xyz2luv(self.spe2xyz())

    def spe2rgb(self) -> NDArray[float64]:
        """spectrum to sRGB"""
        return self._xyz2rgb(self.spe2xyz())
