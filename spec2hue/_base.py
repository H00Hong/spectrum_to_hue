# -*- coding: utf-8 -*-
import csv
import json
import os.path
from typing import Dict, List, Tuple, Union, Literal

import chardet
import openpyxl
import pdfplumber
import wx
import xlrd
from numpy import array, c_, ndarray, vstack


def find_encoding(path: str) -> str:
    """读取csv的编码"""
    detect = chardet.detect(open(path, 'rb').read(4096))
    return detect['encoding']


def find_delimiter(path: str) -> Tuple[str, str]:
    """读取csv的分隔符 return (delimiter, encoding)"""
    sniffer = csv.Sniffer()
    encoding = find_encoding(path)
    with open(path, encoding=encoding) as fp:
        delimiter = sniffer.sniff(fp.read(4096)).delimiter
    return delimiter, encoding


def read_txt(
    path: str,
    header: Union[int, None] = None,
    col: slice = slice(0, None, None)
) -> Tuple[List[List[str]], List[str]]:
    """
    读取csv txt

    Parameters
    ----------
    path: str
        地址
    header: int | None
        表头行号 int 从0开始计数; 若无表头None
    col: slice
        列读取范围

    Returns
    -------
    data: List[List[str]]
        读取的数据
    header: List[str]
        表头
    """
    delimiter, encoding = find_delimiter(path)
    with open(path, encoding=encoding, newline='') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=delimiter)
        if header is None:
            data_header = []
        elif isinstance(header, int):
            for _ in range(header):
                next(csv_reader)
            data_header = next(csv_reader)[col]
        else:
            raise ValueError('header')

        data = [row[col] for row in csv_reader]
    return data, data_header


def read_pdf(path: str, data_ye: int = 0) -> List[List[str]]:
    """
    读取表格pdf
    data_ye为数据跨了几页 0为数据单页
    del_row None为不去除 默认去除第一行
    """
    assert isinstance(data_ye, int)
    data_ye += 1
    pp, pp_, num = [], [], 0
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            del table[0]
            pp_.append(table)
            num += 1
            if num % data_ye == 0:
                y = pp_[0]
                for ii in range(1, data_ye):
                    y += pp_[ii]
                pp.append(y)
                pp_ = []
    y = []
    for ii in pp:
        y.extend(ii)
    pdf.flush_cache()  # 清理缓存 解除占用
    return y


def line_h(parent):
    return wx.StaticLine(parent, style=wx.LI_HORIZONTAL)


def line_v(parent):
    return wx.StaticLine(parent, style=wx.LI_VERTICAL)


def line(parent, style: Literal['h', 'v'] = 'h'):
    if style == 'h':
        return line_h(parent)
    elif style == 'v':
        return line_v(parent)


DIRNAME = os.path.dirname(__file__)
with open(DIRNAME + '/_widgets.json', 'r', encoding='utf-8') as fp:
    WIDGETS_TOTAL = json.load(fp)


def get_setting() -> Dict[str, Union[str, int, bool]]:
    with open(DIRNAME + '/_setting.json', 'r', encoding='utf-8') as fp:
        setting = json.load(fp)
    return setting


def save_setting(setting):
    with open(DIRNAME + '/_setting.json', 'w', encoding='utf-8') as fp:
        json.dump(setting, fp, ensure_ascii=False)
