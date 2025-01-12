# -*- coding: utf-8 -*-
import img
import wx
from mywxwidgets.richtextbase import RichTextBase


class AboutWin(RichTextBase):

    def set_text(self):
        w = self.write
        red = (255,0,0)
        blue = (0,0,255)
        purple = (170,85,255)
        
        w('色度计算和转换操作说明', fontsize=18, bold=True)
        w('-'*40)
        
        w('环境：win7及以上，32位或64位')
        w('输入：待计算的光谱 或 待转换的色度')
        w('输出：计算的色度 或 其他色度')
        w('-'*40)
        
        w('操作说明：', blue, 14)
        w('光谱计算色度'.center(30, '-'), blue)
        w('操作流程:')
        w('1. 导入光谱 -> 2. 选择光源参数和计算项目 -> 3. 在表格中呈现计算结果(保留6位有效数字)，导出结果')
        self.rtc.Newline()
        
        w('---1. 导入光谱：', purple, 14)
        w('\t导入光谱有2种方法:')
        w('\t\t(1) 直接复制')
        w('\t\t(2) `选择文件` -> `导入`')
        # self.rtc.Newline()
        w('\t', new=False)
        w('注意', bold=True, new=False)
        w(': 光谱表格中必须全是', new=False)
        w('数字', red, new=False)
        w('。 光谱表格只接收', new=False)
        w('列向排列', red, new=False)
        w('的数据，并且波长列必须在', new=False)
        w('第一列', red, new=False)
        w('，光谱列必须在波长列的', new=False)
        w('右边', red)
        self.rtc.Newline()
        w('\t(1) 直接复制时： 需要同时', new=False)
        w('复制标题/表头', red, new=False)
        w('，即使原数据没有也需要填写。标题/表头数量需要和光谱一样')
        self.write_img(img.img1)
        w('\t(2) 通过文件导入时： 首先确定文件地址，可以点击选择文件，也可以直接输入。')
        self.write_img(img.img2)
        w('\t\t导入的参数参考下图。导入的文件格式支持', new=False)
        w('xlsx、xls、csv、txt、pdf', red)
        self.write_img(img.img3)
        w('\t程序可以自动识别csv和txt文件的编码和分隔符，如果识别不了，那么请更改文件为', new=False)
        w('utf-8编码和英文逗号分隔符', red, new=False)
        w('。pdf需要3700快速打印的格式，即每一页都有标题、除了大标题和数据表外没有其他内容和格式。')
        self.write_img(img.img4)
        self.rtc.Newline()
        
        w('---2. 选择光源参数和计算项目：', purple, 14)
        w('\t按照需求选择光源参数，第一个选项是光源类型，第二个选项是视场角')
        self.write_img(img.img5)
        w('\t光源类型有 D65、A、C、D50、D55、D75、，视场角有 2°、10°。', new=False)
        w('默认为D65和2°，如果没有特殊要求，那就保持默认不变', red)
        self.rtc.Newline()
        w('\t光源参数选择完成后，点击计算，在弹出的选择计算项目窗口选择计算项目，选择完成后点击确定，程序开始计算色度。')
        self.write_img(img.img6)
        self.rtc.Newline()
        
        w('---3. 输出数据并导出：', purple, 14)
        w('\t计算完成后，表格会中输出选定的计算项目(保留6位有效数字)。注意，sRGB输出的是16进制颜色码，并会在单元格的背景中显示当前的颜色')
        self.write_img(img.img7)
        w('\t之后，可以点击导出，将计算结果导出为csv。在文件中默认16位小数')
        self.rtc.Newline()

        w('色度转换'.center(30, '-'), blue)
        w('确认光源参数，在输入框中输入待转换的色度，点击转换即可完成', new=False)


if __name__ == '__main__':
    app = wx.App()
    frame = AboutWin(None)
    frame.Show()
    app.MainLoop()

