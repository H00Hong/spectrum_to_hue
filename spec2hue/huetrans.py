# -*- coding: utf-8 -*-
from typing import List

import wx
from _base import line_v, WIDGETS_TOTAL
from cie import CIEHueTransform
from numpy import array, concatenate, float64, ndarray


class CIEHueTransform(CIEHueTransform):

    def yanse(self, xyz: ndarray):
        lab = self.xyz2lab(xyz)
        hlab = self.xyz2lab_h(xyz)
        xy_ = self.xyz2yxy(xyz)[1:]
        uv_ = self.xyz2yuv(xyz)[1:]
        luv = self.xyz2luv(xyz)
        ch1 = self.chs(lab)[:2]
        chh = self.chs(hlab)[:2]
        chs2 = self.chs(luv)
        srgb = self.xyz2rgb(xyz)
        rgb16 = self.rgb16(srgb, 1)
        srgb = srgb * 255
        return concatenate([
            xyz.round(3),
            xy_.round(3),
            uv_.round(3),
            lab.round(3),
            ch1.round(3),
            hlab.round(3),
            chh.round(3),
            luv.round(3),
            chs2.round(3),
            srgb.round(3), rgb16
        ])


WIDGETS_LABEL = WIDGETS_TOTAL['huetrans']


class HueTrans(wx.Panel):

    def __init__(self, parent):
        super(HueTrans, self).__init__(parent)
        # self.SetBackgroundColour(wx.Colour(245, 245, 245))
        self._init_ui()
        self._set_font()
        self._layout0()
        self._set_bind()
        self.Centre()
        self.Show()

    def _init_ui(self):
        self.box_out = wx.StaticBox(self, label=WIDGETS_LABEL['box_out'])
        self.box_in = wx.StaticBox(self, label=WIDGETS_LABEL['box_in'])
        # 输入
        self.lab_l00 = wx.StaticText(self, label=WIDGETS_LABEL['label_si'])
        self.lab_l01 = wx.StaticText(self, label=WIDGETS_LABEL['label_vi'])
        self.cb_si = wx.Choice(self,
                               choices=('A', 'D65', 'C', 'D50', 'D55', 'D65'))
        self.cb_vi = wx.Choice(self, choices=('2°', '10°'))
        self.cb_si.SetSelection(1)
        self.cb_vi.SetSelection(0)

        self.cb_l_intype = wx.Choice(self,
                                     choices=('CIE XYZ', 'CIE Yxy', 'CIELAB',
                                              'Hunter Lab', 'sRGB',
                                              'CIE Yu\'v\'', 'CIELUV'))
        self.cb_l_intype_choices_value = (('X', 'Y', 'Z'), ('Y', 'x', 'y'),
                                          ('L*', 'a*', 'b*'), ('L', 'a', 'b'),
                                          ('R', 'G', 'B'), ('Y', 'u\'', 'v\''),
                                          ('L*', 'u*', 'v*'))
        self.cb_l_intype.SetSelection(0)
        lab_l30 = wx.StaticText(self, label='X')
        lab_l30.SetMinSize((25, -1))
        le_l31 = wx.TextCtrl(self)
        lab_l40 = wx.StaticText(self, label='Y')
        lab_l40.SetMinSize((25, -1))
        le_l41 = wx.TextCtrl(self)
        lab_l50 = wx.StaticText(self, label='Z')
        lab_l50.SetMinSize((25, -1))
        le_l51 = wx.TextCtrl(self)

        self.btn_l6 = wx.Button(self, label=WIDGETS_LABEL['button'])
        self.btn_l6.SetMinSize((-1, 65))
        self.lab_input = [lab_l30, lab_l40, lab_l50]
        self.le_input = [le_l31, le_l41, le_l51]

        self.labs = self.lab_input.copy()
        self.le_output: List[wx.TextCtrl] = []
        # 输出
        titles = ('CIE XYZ xy u\'v\'', 'CIELAB', 'Hunter Lab', 'CIELUV',
                  'sRGB')
        lst = (('X', 'Y', 'Z', 'x', 'y', 'u\'', 'v\''),
               ('L*', 'a*', 'b*', 'C*', 'h'), ('L', 'a', 'b', 'C', 'h'),
               ('L*', 'a*', 'b*', 'C*', 'h', 's'), ('R', 'G', 'B', '16'))
        self.layoutr = wx.StaticBoxSizer(self.box_out, wx.HORIZONTAL)
        for t, lst in zip(titles, lst):
            labs1, les1, layout1 = self._init_ui_r1(t, lst)
            self.labs.extend(labs1)
            self.le_output.extend(les1)
            self.layoutr.Add(layout1, 1, wx.ALL | wx.EXPAND, 3)

    def _init_ui_r1(self, title: str, lab_list: List[str]):
        labs = [wx.StaticText(self, label=title)]
        les: List[wx.TextCtrl] = []
        layout1 = wx.BoxSizer(wx.VERTICAL)
        layout1.Add(labs[0], 0, wx.ALL | wx.ALIGN_CENTER, 3)

        for label in lab_list:
            lab = wx.StaticText(self, label=label)
            lab.SetMinSize((25, -1))
            le = wx.TextCtrl(self)
            labs.append(lab)
            les.append(le)
            layout1_1 = wx.BoxSizer(wx.HORIZONTAL)
            layout1_1.Add(lab, 0, wx.ALL | wx.ALIGN_CENTER, 0)
            layout1_1.Add(le, 1, wx.ALL | wx.ALIGN_CENTER, 0)
            layout1.Add(layout1_1, 1, wx.ALL | wx.EXPAND, 3)
        return labs, les, layout1

    def _set_bind(self):
        self.btn_l6.Bind(wx.EVT_BUTTON, self._on_btn)
        self.cb_l_intype.Bind(wx.EVT_CHOICE, self._on_cb)

    def _set_font(self):
        FONT0 = wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                        wx.FONTWEIGHT_NORMAL, False, 'Microsoft Yahei')
        FONT1 = wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                        wx.FONTWEIGHT_NORMAL, False, 'Microsoft Yahei')
        for i in self.labs:
            i.SetFont(FONT0)
        for i in self.le_input:
            i.SetFont(FONT0)
        for i in self.le_output:
            i.SetFont(FONT0)
        # self.lab_l1.SetFont(FONT1)
        self.box_in.SetFont(FONT1)
        # self.lab_r0.SetFont(FONT1)
        self.box_out.SetFont(FONT1)
        self.btn_l6.SetFont(FONT1)
        self.lab_l00.SetFont(FONT0)
        self.lab_l01.SetFont(FONT0)
        self.cb_si.SetFont(FONT0)
        self.cb_vi.SetFont(FONT0)
        self.cb_l_intype.SetFont(FONT0)

    def _layout0(self):
        self.layout = wx.BoxSizer(wx.VERTICAL)
        self.layout0 = wx.BoxSizer(wx.HORIZONTAL)
        self.layoutl = self._layout_l()

        self.layout0.Add(self.layoutl, 0, wx.ALL, 3)
        self.layout0.Add(line_v(self), 0, wx.ALL | wx.EXPAND, 10)
        self.layout0.Add(self.layoutr, 1, wx.ALL | wx.EXPAND, 3)
        self.layout.Add(self.layout0, 0, wx.ALL | wx.EXPAND, 0)
        self.layout.Add(wx.StaticText(self), 1, wx.ALL | wx.EXPAND, 0)
        self.SetSizer(self.layout)

    def _layout_l(self):
        layout1 = wx.GridSizer(0, 2, 0, 0)
        # layout_h0 = wx.BoxSizer(wx.HORIZONTAL)
        layout1.Add(self.lab_l00, 0, wx.ALL | wx.ALIGN_CENTER, 0)
        layout1.Add(self.lab_l01, 0, wx.ALL | wx.ALIGN_CENTER, 0)
        # layout_h1 = wx.BoxSizer(wx.HORIZONTAL)
        layout1.Add(self.cb_si, 0, wx.ALL | wx.ALIGN_CENTER, 0)
        layout1.Add(self.cb_vi, 0, wx.ALL | wx.ALIGN_CENTER, 0)

        layout2 = wx.StaticBoxSizer(self.box_in, wx.VERTICAL)
        layout2.Add(self.cb_l_intype, 0, wx.ALL | wx.EXPAND, 3)
        for lab, le in zip(self.lab_input, self.le_input):
            layout_h4 = wx.BoxSizer(wx.HORIZONTAL)
            layout_h4.Add(lab, 0, wx.ALL | wx.ALIGN_CENTER, 3)
            layout_h4.Add(le, 0, wx.ALL | wx.ALIGN_CENTER, 3)
            layout2.Add(layout_h4, 0, wx.ALL | wx.EXPAND, 3)

        layout = wx.BoxSizer(wx.VERTICAL)
        layout.Add(layout1, 0, wx.EXPAND, 3)
        layout.Add(layout2, 0, wx.EXPAND, 3)
        layout.Add(self.btn_l6, 0, wx.EXPAND, 3)
        return layout

    def _on_cb(self, event):
        # 获取当前选择的项
        selection: int = self.cb_l_intype.GetSelection()
        ss = self.cb_l_intype_choices_value[selection]
        # print(selection)
        for s, lab in zip(ss, self.lab_input):
            lab.SetLabel(s)

    def _on_btn(self, event):
        si = self.cb_si.GetStringSelection()
        vi = self.cb_vi.GetSelection() * 8 + 2
        selection = self.cb_l_intype.GetStringSelection()
        ciet = CIEHueTransform(si, vi)
        s = array([le.GetValue() for le in self.le_input], float64)
        if selection == 'CIE XYZ':
            pass
        elif selection == 'CIE Yxy':
            s = ciet.yxy2xyz(s)
        elif selection == 'CIELAB':
            s = ciet.lab2xyz(s)
        elif selection == 'Hunter Lab':
            s = ciet.lab_h2xyz(s)
        elif selection == 'sRGB':
            s = ciet.rgb2xyz(s / 255)
        elif selection == 'CIE Yu\'v\'':
            s = ciet.yuv2xyz(s)
        else:  # if selection == 'CIELUV':
            s = ciet.luv2xyz(s)

        dat = ciet.yanse(s)
        # print(dat)
        for d, v in zip(dat, self.le_output):
            v.SetValue(d)


if __name__ == '__main__':
    app = wx.App()
    win = wx.Frame(None, title='色度转换', size=(1200, 800))
    main = HueTrans(win)
    win.Centre()
    win.Show()
    app.MainLoop()
