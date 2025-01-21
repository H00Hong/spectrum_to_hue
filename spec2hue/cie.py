# -*- coding: utf-8 -*-
"""
CIE1931|1964|1976色度计算
"""
from typing import Literal, Tuple, Union

from cie_data import (Mrgb, Mrgb2, aKabHunter, aStandardIlluminant,
                      aWhitePoint, aWhitePointHunter, axyzL)
from interpolate import interp1d
from numpy import (arange, arctan2, asarray, c_, ceil, clip, diff, float64,
                   floor, nan_to_num, ndarray, pi, sqrt, all)
from numpy.typing import NDArray

aSIKeys = ('A', 'D65', 'C', 'D50', 'D55', 'D75')
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
        raise ValueError(f'ndim must be 1 or 2, but got {s.ndim}')
    if s.shape[0] != 3:
        raise ValueError(f'shape[0] must be 3, but got {s.shape[0]}')
    return s


class CIEHueTransform:
    """
    CIE1931|1964|1976 hue transform.

    Parameters
    ----------
    SI : {'A','D65','C','D50','D55','D75'}, default 'D65'
        The Standard Illuminant, {'A', 'D65', 'C', 'D50', 'D55', 'D75'}, default: 'D65'.
    vi : {2, 10}, default 2
        The Viewing Angle, {2, 10}, default: 2.

    Methods
    -------
    xyz2lab(XYZ):
        CIE XYZ to CIE 1976(L*a*b*)colour space
    xyz2lab_h(XYZ):
        CIE XYZ to HunterLab
    xyz2yuv(XYZ):
        CIE XYZ to CIE Yu'v'
    xyz2yxy(XYZ):
        CIE XYZ to CIE Yxy
    xyz2luv(XYZ):
        CIE XYZ to CIE 1976 (L*u*v*) colour space
    xyz2rgb(XYZ):
        CIE XYZ to sRGB
    lab2xyz(Lab):
        CIE 1976 (L*a*b*) colour space to CIE XYZ
    lab_h2xyz(Lab):
        HunterLab to CIE XYZ
    yuv2xyz(Yuv):
        CIE Yu'v' to CIE XYZ
    yxy2xyz(Yxy):
        CIE Yxy to CIE XYZ
    luv2xyz(Luv):
        CIE 1976 (L*u*v*) colour space to CIE XYZ
    rgb2xyz(sRGB):
        sRGB to CIE XYZ
    chs(Lab|Luv):
        CIE 1976 (L*a*b*)|(L*u*v*) colour space to Chs
    lab2rgb(Lab):
        CIE 1976 (L*a*b*) colour space to sRGB
    rgb2lab(sRGB):
        sRGB to CIE 1976 (L*a*b*) colour space
    rgb16(sRGB):
        sRGB to 16-sRGB
    rbg16_(16-sRGB):
        16-sRGB to sRGB
    """

    _wp: Tuple[NDArray[float64], NDArray[float64]]
    _wp_h: Tuple[NDArray[float64], NDArray[float64]]
    __slots__ = ['_wp', '_wp_h', '_kab', 'info']

    def __init__(self,
                 si: Literal['A', 'D65', 'C', 'D50', 'D55', 'D75',
                             'a', 'd65', 'c', 'd50', 'd55', 'd75'] = 'D65',
                 vi: Literal[2, 10] = 2):
        if not isinstance(si, str):
            raise TypeError(f'{self.__class__}: 光源输入类型错误, 请输入字符串')
        si = si.upper()
        if si not in aSIKeys:
            raise ValueError(f'{self.__class__}: 光源种类错误')
        if vi != 2 and vi != 10:
            raise ValueError(f'{self.__class__}: 视场角错误')

        self.info = {'SI': si, 'VI': vi}
        si_v = self._get_si()
        vi_v = self._get_vi()
        wp = aWhitePoint[vi_v, :, si_v]
        wp_h = aWhitePointHunter[vi_v, :, si_v]
        self._wp = (wp, wp[:, None])
        self._wp_h = (wp_h, wp_h[:, None])
        self._kab: NDArray[float64] = aKabHunter[vi_v, :, si_v]

    def _get_si(self) -> int:
        return aSIKeys.index(self.info['SI'])

    def _get_vi(self) -> int:
        return (self.info['VI'] - 2) // 8

    def xyz2lab(self, xyz: ndarray) -> NDArray[float64]:
        """
        CIE XYZ to CIELAB.

        Parameters
        ----------
        xyz : array_like of float 1-dim or 2-dim
            CIE XYZ matrix, ``xyz.shape[0] == 3``,
            axis0 is XYZ, axis1 is input item(if 2-dim)

            1-dim:
                +---+---+---+ 
                | X | Y | Z |
                +---+---+---+
            2-dim:
                +-----+-----+
                | X_a | X_b |
                +-----+-----+
                | Y_a | Y_b |
                +-----+-----+
                | Z_a | Z_b |
                +-----+-----+

        Returns
        -------
        NDArray[float64] 1-dim or 2-dim
            CIELAB matrix, shape is same as `xyz`, axis0 is L* a* b*, axis1 is input item(if 2-dim)
        """
        wp = self._wp[xyz.ndim - 1]
        x1, y1, z1 = _ff(xyz / wp)
        L = 116 * y1 - 16
        a = 500 * (x1 - y1)
        b = 200 * (y1 - z1)
        return asarray((L, a, b))

    def xyz2lab_h(self, xyz: ndarray) -> NDArray[float64]:
        x1, y1, z1 = xyz / self._wp_h[xyz.ndim - 1]
        y2 = sqrt(y1)
        L = 100 * y2
        a = self._kab[0] * (x1 - y1) / y2
        b = self._kab[1] * (y1 - z1) / y2
        return asarray((L, a, b))

    def xyz2yuv(self, xyz: ndarray) -> NDArray[float64]:
        x, y, z = xyz
        fm = x + 15 * y + 3 * z
        return asarray((y, 4 * x / fm, 9 * y / fm))

    def xyz2yxy(self, xyz: ndarray) -> NDArray[float64]:
        temp = xyz[[0, 1]] / xyz.sum(axis=0)
        return asarray((xyz[1], *temp))

    def xyz2luv(self, xyz: ndarray) -> NDArray[float64]:
        uv = self._xyz2yuv(xyz)[1:]
        uvn = self._xyz2yuv(self._wp[xyz.ndim - 1])[1:]
        L = _ff(xyz[1] / 100) * 116 - 16
        u, v = 13 * L * (uv - uvn)
        return asarray((L, u, v))

    def xyz2rgb(self, xyz: ndarray) -> NDArray[float64]:
        y1 = Mrgb @ xyz / 100
        y2 = 1.055 * nan_to_num(y1**(1 / 2.4)) - 0.058025  # 1.055 * 0.055
        y3 = 12.92 * y1
        # http://www.brucelindbloom.com/index.html?WorkingSpaceInfo.html
        res = y2 * (y1 > 0.0031308) + y3 * (y1 <= 0.0031308)
        return clip(res, 0, 1)

    def chs(self, luv: ndarray) -> NDArray[float64]:
        """
        get C, h, s with CIELAB or CIELUV.
        """
        L, u, v = luv
        C = sqrt(u**2 + v**2)
        h = arctan2(v, u) * 180 / pi
        s = C / L
        return asarray((C, h, s))

    def lab2xyz(self, lab: ndarray) -> NDArray[float64]:
        L, a, b = lab
        y1 = (L + 16) / 116
        x1 = a / 500 + y1
        z1 = y1 - b / 200
        return _ff_(asarray((x1, y1, z1))) * self._wp[lab.ndim - 1]

    def lab_h2xyz(self, lab_h: ndarray) -> NDArray[float64]:
        L, a, b = lab_h
        y0 = L**2 / 10000
        x0 = a / self._kab[0] * L / 100 + y0
        z0 = y0 - b / self._kab[1] * L / 100
        return asarray((x0, y0, z0)) * self._wp_h[lab_h.ndim - 1]

    def luv2xyz(self, luv: ndarray) -> NDArray[float64]:
        uvn = self._xyz2yuv(self._wp[luv.ndim - 1])[1:]
        L = luv[0]
        u_, v_ = luv[1:] / 13 / L + uvn
        Y = _ff_((L + 16) / 116) * 100
        X = 9 / 4 * u_ / v_ * Y
        Z = 3 * Y / v_ - X / 3 - 5 * Y
        return asarray((X, Y, Z))

    def yxy2xyz(self, yxy: ndarray) -> NDArray[float64]:
        all_sum = yxy[0] / yxy[2]
        return asarray((yxy[1] * all_sum, yxy[0], (1 - yxy[1] - yxy[2]) * all_sum))

    def yuv2xyz(self, yuv: ndarray) -> NDArray[float64]:
        # (y, 4 * x / fm, 9 * y / fm)
        y = yuv[0]
        fm = 9 * y / yuv[2]  # x + 15 * y + 3 * z
        x = yuv[1] * fm / 4
        return asarray((x, y, (fm - x - 15 * y) / 3))

    def rgb2xyz(self, rgb: ndarray) -> NDArray[float64]:
        rgb = clip(rgb, 0, 1)
        y1 = rgb / 12.92
        y2 = ((rgb + 0.055) / 1.055)**2.4
        yy = y1 * (rgb <= 0.04045) + y2 * (rgb > 0.04045)
        return Mrgb2 @ yy * 100

    def rgb16(self, rgb: ndarray, upper = 255) -> ndarray:
        """
        RGB[int,int,int] 转 16进制.

        Parameters
        ----------
        rgb : array_like of float 1-dim or 2-dim
            RGB matrix, ``rgb.shape[0] == 3``, range is 0-`upper`, 
            axis0 is R G B, axis1 is input item(if 2-dim)

            1-dim:
                +---+---+---+ 
                | R | G | B |
                +---+---+---+
            2-dim:
                +-----+-----+
                | R_a | R_b |
                +-----+-----+
                | G_a | G_b |
                +-----+-----+
                | B_a | B_b |
                +-----+-----+

        upper : float, default 255
            `rgb` value upper limit, default is 255

        Returns
        -------
        NDArray[str] 1-dim
            RGB list
        """
        if upper != 255:
            rgb = (rgb/upper*255).round()
        rgb = clip(rgb.astype(int), 0, 255)
        if rgb.ndim == 1 or rgb.shape[0] == 1:
            rgb = rgb.reshape([3, 1])
        s = []
        for ic in range(rgb.shape[1]):
            ss = '#'
            for ir in range(rgb.shape[0]):
                s0 = hex(rgb[ir, ic])[-2:]
                ss += s0.replace('x', '0')
            s.append(ss)
        return asarray(s)

    def rgb16_(self,
               rgbtxt: Union[ndarray, list, str],
               upper = 255) -> NDArray[float64]:
        """
        16进制颜色码 转 RGB[float,float,float].

        Parameters
        ----------
        rgbtxt : array_like of str or str
            RGB string list or a RGB string
        upper : float, default 255
            `rgbtxt` value upper limit, default is 255

        Returns
        -------
        NDArray[float64] 1-dim or 2-dim
            sRGB matrix, range is 0-1,  
            axis0 is R G B, axis1 is input item(if 2-dim)
        """
        if isinstance(rgbtxt, str):
            rgbtxt = [rgbtxt]
        for ii, val in enumerate(rgbtxt):
            if val[0] != '#' or len(val) != 7:
                raise ValueError('sRGB格式错误, 请输入带#的16进制颜色码')
            rgb = asarray([
                int(val[1:3], 16),
                int(val[3:5], 16),
                int(val[5:7], 16)
            ], dtype=float64)
            if ii == 0:
                rgblst = rgb
            else:
                rgblst = c_[rgblst, rgb]
        return clip(rgblst / upper, 0, 1)


class CIE(CIEHueTransform):
    """
    CIE1931|1964|1976 hue calculator.

    Parameters
    ----------
    spec : ndarray or list or tuple or DataFrame or Series or dict
        The spectrum, 2-dim matrix or dict.
        If `spec` is dict, `spec` must contain 'wavelength' and 'spec'
    SI : {'D65', 'A', 'C', 'D50', 'D55', 'D75'}, default 'D65'
        The Standard Illuminant, {'A', 'D65', 'C', 'D50', 'D55', 'D75'} not case-sensitive, default: 'D65'.
    vi : {2, 10}, default 2
        The Viewing Angle, {2, 10}, default: 2.
    unit : {'nm', 'um', 'μm'}, default 'nm'
        The wavelength unit of the spectrum, {'nm', 'um', 'μm'}, default: 'nm'.
    upper : {1, 100}, default 100
        The upper limit of the spectrum, {1, 100}, default: 100.

    Methods
    -------
    spec2xyz():
        spectrum to CIE XYZ
    spec2yxy():
        spectrum to CIE Yxy
    spec2yuv():
        spectrum to CIE Yuv
    spec2lab():
        spectrum to CIE 1976 (L*a*b*) colour space
    spec2lab_h():
        spectrum to HunterLab
    spec2luv():
        spectrum to CIE 1976 (L*u*v*) colour space
    spec2rgb():
        spectrum to sRGB
    xyz2lab(XYZ):
        CIE XYZ to CIE 1976(L*a*b*)colour space
    xyz2lab_h(XYZ):
        CIE XYZ to HunterLab
    xyz2yuv(XYZ):
        CIE XYZ to CIE Yu'v'
    xyz2yxy(XYZ):
        CIE XYZ to CIE Yxy
    xyz2luv(XYZ):
        CIE XYZ to CIE 1976 (L*u*v*) colour space
    xyz2rgb(XYZ):
        CIE XYZ to sRGB
    lab2xyz(Lab):
        CIE 1976 (L*a*b*) colour space to CIE XYZ
    lab_h2xyz(Lab):
        HunterLab to CIE XYZ
    yuv2xyz(Yuv):
        CIE Yu'v' to CIE XYZ
    yxy2xyz(Yxy):
        CIE Yxy to CIE XYZ
    luv2xyz(Luv):
        CIE 1976 (L*u*v*) colour space to CIE XYZ
    rgb2xyz(sRGB):
        sRGB to CIE XYZ
    chs(Lab|Luv):
        CIE 1976 (L*a*b*)|(L*u*v*) colour space to Chs
    lab2rgb(Lab):
        CIE 1976 (L*a*b*) colour space to sRGB
    rgb2lab(sRGB):
        sRGB to CIE 1976 (L*a*b*) colour space
    rgb16(sRGB):
        sRGB to 16-sRGB
    rbg16_(16-sRGB):
        16-sRGB to sRGB
    """

    __slots__ = ['spec', 'si0', 'xyzl0', 'sxyzl', 'spec_interp']

    def __init__(self, spec: Union[ndarray, list, tuple],
                 si: Literal['A', 'D65', 'C', 'D50', 'D55', 'D75',
                             'a', 'd65', 'c', 'd50', 'd55', 'd75'] = 'D65',
                 vi: Literal[2, 10] = 2,
                 unit: Literal['nm', 'um', 'μm'] = 'nm',
                 upper: Literal[1, 100] = 100):
        super().__init__(si, vi)
        if isinstance(spec, (ndarray, list, tuple)):
            spec = asarray(spec)
            spec = spec[spec[:, 0].argsort()]
            w0 = spec[:, 0]
            spec = spec[:, 1:]
        else:
            raise TypeError(f'{self.__class__}: spec 格式错误')

        if upper == 100:
            assert all(spec <= 100)
        elif upper == 1:
            assert all(spec <= 1)
            spec = spec * 100
        else:
            raise ValueError(f'{self.__class__}: upper 错误, 请输入 1 或 100')
        if unit == 'nm':
            pass
        elif unit in ('um', 'μm'):
            w0 = w0 * 1000
        else:
            raise ValueError(f'{self.__class__}: unit 错误, 请输入 \'nm\'、\'um\' 或 \'μm\'')
        wn = w0.min()
        wm = w0.max()
        self.spec_interp = interp1d(w0, spec, axis=0, kind='cubic')

        dy = diff(w0)
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
        self.info['wavelength_step'] = step
        self.info['wavelength_range'] = (wn, wm)
        self.info['item_number'] = spec.shape[-1]
        w1 = arange(wn, wm+step, step, int)

        self.spec: NDArray[float64] = spec if all(w1 == w0) else self.spec_interp(w1)
        w1 -= 380
        self.si0: NDArray[float64] = aStandardIlluminant[w1, 1 + self._get_si()]
        self.xyzl0: NDArray[float64] = axyzL[self._get_vi(), w1, 1:].T
        self.sxyzl: NDArray[float64] = self.si0 * self.xyzl0

    def spec2xyz(self) -> NDArray[float64]:
        """spectrum to CIE XYZ."""
        # sumXYZ = self.sxyzl@t/100
        # k = 100/np.sum(sxyz[1])
        return self.sxyzl @ self.spec / self.sxyzl[1].sum()

    def spec2yxy(self) -> NDArray[float64]:
        """spectrum to CIE Yxy."""
        return self._xyz2yxy(self.spec2xyz())

    def spec2yuv(self) -> NDArray[float64]:
        """spectrum to CIE Yuv."""
        return self._xyz2yuv(self.spec2xyz())

    def spec2lab(self) -> NDArray[float64]:
        """spectrum to CIELAB."""
        return self._xyz2lab(self.spec2xyz())

    def spec2lab_h(self) -> NDArray[float64]:
        """spectrum to HunterLAB."""
        return self._xyz2lab_h(self.spec2xyz())

    def spec2luv(self) -> NDArray[float64]:
        """spectrum to CIELUV."""
        return self._xyz2luv(self.spec2xyz())

    def spec2rgb(self) -> NDArray[float64]:
        """spectrum to sRGB."""
        return self._xyz2rgb(self.spec2xyz())
