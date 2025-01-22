# -*- coding: utf-8 -*-
import huetrans
import spec2hue
import wx
from _base import WIDGETS_TOTAL

WIDGETS_LABEL = WIDGETS_TOTAL['main']


class MainWin(wx.Frame):

    def __init__(self):
        super(MainWin, self).__init__(None,
                                      size=(1010, 600),
                                      title='色度计算和转换v4.3 —— 洪溢凡,2025.1.22')
        # self.SetBackgroundColour(wx.Colour(245, 245, 245))
        self.SetMinSize((1000, 430))
        self._init_ui()
        self.Centre()
        self.Show()

    def _init_ui(self):
        # 创建一个Notebook控件
        notebook = wx.Notebook(self)
        notebook.SetFont(
            wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                    wx.FONTWEIGHT_NORMAL, False, 'Microsoft Yahei'))
        # 创建第一个Tab页
        self.tab1 = spec2hue.Spec2Hue(notebook)
        # 创建第二个Tab页
        tab2 = huetrans.HueTrans(notebook)
        # 将Tab页添加到Notebook中
        notebook.AddPage(self.tab1, WIDGETS_LABEL['tab1'])
        notebook.AddPage(tab2, WIDGETS_LABEL['tab2'])
        # 设置Notebook的布局
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(notebook, 1, wx.EXPAND | wx.ALL, 0)
        self.SetSizer(sizer)


if __name__ == '__main__':
    app = wx.App()
    MainWin()
    app.MainLoop()
