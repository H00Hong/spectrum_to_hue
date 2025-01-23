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
from _base import *


path = r'D:\HONG\办公自动化\新建文件夹 (2)\数据打印.xlsx'
app = wx.App()
win = ReadFileData(None, path)
win.ShowModal()
app.MainLoop()