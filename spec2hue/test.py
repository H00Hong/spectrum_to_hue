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


WIDGETS_LABEL = {
    'left': {
        '0_label_input': {'label': '输入'},
        '0_label_none1': {'label': ''},
        '0_button_instructions': {'label': '操作说明'},
        '1_button_select': {'label': '选择文件'},
        '1_text_import': {'value': ''},
        '1_button_import': {'label': ' 导  入 '},
        '2_label_spectrum': {'label': '光谱'},
        '2_line_1': {'style': 'h'},
        '3_GridWithHeader_spectrum': {'subject': '(20, 3)'},
        '4_label_none2': {'label': ''},
        '4_label_wavelength.unit': {'label': '波长单位'},
        '4_choice_wavelength.unit': {'choices': ('nm', 'μm')},
        '4_label_spectrum.upper': {'label': '光谱上限'},
        '4_choice_spectrum.upper': {'choices': ('1', '100')},
    },
    'right': {
        '0_label_output': {'label': '输出'},
        '1_label_si': {'label': '光源参数: '},
        '1_choice_si': {'choices': ('A', 'D65', 'C', 'D50', 'D55', 'D75')},
        '1_choice_vi': {'choices': ('2°', '10°')},
        '1_line_2': {'style': 'v'},
        '1_label_none3': {'label': ''},
        '1_button_calculate': {'label': '计 算'},
        '2_label_calculate': {'label': '计算输出'},
        '2_line_3': {'style': 'h'},
        '3_Grid_output': {'read_only': True},
        '4_label_none4': {'label': ''},
        '4_button_save': {'label': '导 出'}
    }
}
with open(os.path.dirname(__file__) + '/spec2hue.json',
              'w',
              encoding='utf-8') as fp:
        json.dump(WIDGETS_LABEL, fp, ensure_ascii=False)
