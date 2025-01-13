# -*- coding: utf-8 -*-
import csv
import json
import os.path
from typing import List, Tuple, Union, Dict

import about
import chardet
import openpyxl
import pdfplumber
import numpy as np
import wx
import xlrd
from cie import CIE
from mywxwidgets.grid.gridnumpy import Grid, GridWithHeader
from numpy import array, c_, ndarray, vstack


def _line_h(parent):
    return wx.StaticLine(parent, style=wx.LI_HORIZONTAL)


def _line_v(parent):
    return wx.StaticLine(parent, style=wx.LI_VERTICAL)


def get_setting() -> Dict[str, int | bool]:
    with open(os.path.dirname(__file__) + '/_setting.json',
              'r',
              encoding='utf-8') as fp:
        setting = json.load(fp)
    return setting


def save_setting(setting):
    with open(os.path.dirname(__file__) + '/_setting.json',
              'w',
              encoding='utf-8') as fp:
        json.dump(setting, fp, ensure_ascii=False)


CHECKBOX_TITLE = ('X', 'Y', 'Z', 'x', 'y', 'z', 'CIELAB-L*', 'CIELAB-a*',
                  'CIELAB-b*', 'CIELAB-C*_ab', 'CIELAB-h_ab', 'Hunter L',
                  'Hunter a', 'Hunter b', 'Hunter C_ab', 'Hunter h_ab', 'sRGB',
                  'u\'', 'v\'', 'w\'', 'CIELUV-L*', 'CIELUV-u*', 'CIELUV-v*',
                  'CIELUV-C*_uv', 'CIELUV-h_uv', 'CIELUV-s_uv')
CHECKBOX_LABEL = ('X', 'Y', 'Z', 'x', 'y', 'z', 'L*', 'a*', 'b*', 'C*_ab',
                  'h_ab', 'L', 'a', 'b', 'C_ab', 'h_ab', 'sRGB', 'u\'', 'v\'',
                  'w\'', 'L*', 'u*', 'v*', 'C*_uv', 'h_uv', 's_uv')
# CHECKBOX_BOOL = (True, True, True, False, False, False, True, True, True,
#                  False, False, False, False, False, False, False, True, False,
#                  False, False, False, False, False, False, False, False)
CHECKBOX_DICT = dict(zip(CHECKBOX_TITLE, CHECKBOX_LABEL))


class CalcItems(wx.Dialog):

    def __init__(self, parent, c: bool) -> None:
        super(CalcItems, self).__init__(parent,
                                        title='选择计算项目',
                                        size=(500, 500))
        self.setting = get_setting()
        self._c = c
        self._init_ui()
        self.Centre()

    def _init_ui(self):
        self.lab3 = wx.StaticText(self, label='CIE XYZ')
        self.lab6 = wx.StaticText(self, label='CIE xyz')
        self.lab9 = wx.StaticText(self, label='CIELAB')
        self.lab12 = wx.StaticText(self, label='Hunter Lab')
        self.cb15 = wx.CheckBox(self, label='sRGB')
        self.lab17 = wx.StaticText(self, label='CIE u\'v\'w\'')
        self.lab20 = wx.StaticText(self, label='CIELUV')
        self.lab230 = wx.StaticText(self, label='')
        self.btn231 = wx.Button(self, label='确定')
        self.btn232 = wx.Button(self, label='取消')

        self.checkBoxs = {
            k: wx.CheckBox(self, label=l)
            for k, l in CHECKBOX_DICT.items()
        }
        if self._c:
            self.cb_yi = wx.CheckBox(self, label='YI')
            self.cb_yi.SetValue(self.setting['YI'])
        for k, v in self.checkBoxs.items():
            v.SetValue(self.setting[k])
        self._set_font()
        self._laypout_0()

        self.Bind(wx.EVT_BUTTON, self._on_ok, self.btn231)
        self.Bind(wx.EVT_BUTTON, self._on_cancel, self.btn232)

    def _on_ok(self, event):
        self.result: Dict[str, bool] = {}
        for k, v in self.checkBoxs.items():
            b: bool = v.GetValue()
            self.setting[k] = b
            self.result[k] = b
        if self._c:
            b = self.cb_yi.GetValue()
            self.setting['YI'] = b
            self.result['YI'] = b
        save_setting(self.setting)
        self.EndModal(wx.ID_OK)  # 这里传入的参数会在 ShowModal return

    def _on_cancel(self, event):
        self.EndModal(wx.ID_CANCEL)  # 这里传入的参数会在 ShowModal return

    def _layout_1(self, layout1: wx.BoxSizer):
        layout10 = wx.BoxSizer(wx.VERTICAL)
        layout10.Add(_line_h(self), 0, wx.EXPAND | wx.ALL, 3)
        layout11 = wx.BoxSizer(wx.VERTICAL)
        layout11.Add(_line_h(self), 0, wx.EXPAND | wx.ALL, 3)

        for lab, cb_t in zip(
            (self.lab3, self.lab6, self.lab17),
            (('X', 'Y', 'Z'), ('x', 'y', 'z'), ('u\'', 'v\'', 'w\''))):
            layout10.Add(lab, 0, wx.ALL, 3)
            layout = wx.BoxSizer(wx.HORIZONTAL)
            for i in cb_t:
                layout.Add(self.checkBoxs[i], 1, wx.ALL | wx.EXPAND, 3)
            layout10.Add(layout, 1, wx.EXPAND | wx.ALL, 3)
            layout10.Add(_line_h(self), 0, wx.EXPAND | wx.ALL, 3)

        for lab, cb_t in zip(
            (self.lab9, self.lab12, self.lab20),
            (('CIELAB-L*', 'CIELAB-a*', 'CIELAB-b*', 'CIELAB-C*_ab',
              'CIELAB-h_ab'), ('Hunter L', 'Hunter a', 'Hunter b',
                               'Hunter C_ab', 'Hunter h_ab'),
             ('CIELUV-L*', 'CIELUV-u*', 'CIELUV-v*', 'CIELUV-C*_uv',
              'CIELUV-h_uv', 'CIELUV-s_uv'))):
            layout11.Add(lab, 0, wx.ALL, 3)
            layout = wx.GridSizer(0, 3, 0, 0)
            for i in cb_t:
                layout.Add(self.checkBoxs[i], 1, wx.ALL, 3)
            layout11.Add(layout, 1, wx.EXPAND | wx.ALL, 3)
            layout11.Add(_line_h(self), 0, wx.EXPAND | wx.ALL, 3)

        layout1.Add(layout10, 1, wx.EXPAND | wx.ALL, 3)
        layout1.Add(_line_v(self), 0, wx.EXPAND | wx.ALL, 3)
        layout1.Add(layout11, 1, wx.EXPAND | wx.ALL, 3)

    def _laypout_0(self):
        layout0 = wx.BoxSizer(wx.VERTICAL)
        layout1 = wx.BoxSizer(wx.HORIZONTAL)
        self._layout_1(layout1)
        layout0.Add(layout1, 1, wx.EXPAND | wx.ALL, 3)

        if self._c:
            layout = wx.BoxSizer(wx.HORIZONTAL)
            layout.Add(self.checkBoxs['sRGB'], 0, wx.ALL, 3)
            layout.Add(self.cb_yi, 0, wx.ALL, 3)
            layout0.Add(layout, 0, wx.ALL)
        else:
            layout0.Add(self.checkBoxs['sRGB'], 0, wx.ALL, 3)
        layout0.Add(_line_h(self), 0, wx.EXPAND | wx.ALL, 3)

        layout1 = wx.BoxSizer(wx.HORIZONTAL)
        layout1.Add(self.lab230, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 3)
        layout1.Add(self.btn231, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 3)
        layout1.Add(self.btn232, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 3)
        layout0.Add(layout1, 0, wx.EXPAND | wx.ALL, 3)
        self.SetSizer(layout0)

    def _set_font(self):
        FONT0 = wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                        wx.FONTWEIGHT_NORMAL, False, 'Microsoft Yahei')
        self.SetFont(FONT0)
        # self.lab0.SetFont(FONT0)
        self.lab3.SetFont(FONT0)
        self.lab6.SetFont(FONT0)
        self.lab9.SetFont(FONT0)
        self.lab12.SetFont(FONT0)
        self.lab17.SetFont(FONT0)
        self.lab20.SetFont(FONT0)
        for v in self.checkBoxs.values():
            v.SetFont(FONT0)
        self.btn231.SetFont(FONT0)
        self.btn232.SetFont(FONT0)
        if self._c:
            self.cb_yi.SetFont(FONT0)


if __name__ == '__main__':
    app = wx.App()
    frame = CalcItems(None, True)
    frame.ShowModal()
    app.MainLoop()
