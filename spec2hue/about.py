# -*- coding: utf-8 -*-
import json

import wx
from mywxwidgets.richtextbase import RichTextBase


class AboutWin(RichTextBase):

    def set_text(self):
        # w = self.write
        # red = (255,0,0)
        # blue = (0,0,255)
        # purple = (170,85,255)
        with open('./_about.json', 'r', encoding='utf-8') as fp:
            text = json.load(fp)
        keys = sorted(text)
        for i in keys:
            if 'img' in text[i]:
                self.write_img(text[i]['img'])
            else:
                self.write(**text[i])


if __name__ == '__main__':
    app = wx.App()
    frame = AboutWin(None)
    frame.Show()
    app.MainLoop()

