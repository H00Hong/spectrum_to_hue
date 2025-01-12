# -*- coding: utf-8 -*-
import base64
from PIL import Image
import io


def image2base64(image_path, format='PNG') -> str:
    # 打开图片文件
    with Image.open(image_path) as img:
        # 将图片转换为字节流
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format=format)
        # 转换为Base64
        img_base64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
    return img_base64


def write_base64(dic:dict[str, str], path:str='output_base64.py') -> None:
    with open(path, 'w') as file:
        for k, v in dic.items():
            file.write(f'{k} = "{v}"\n')


if __name__ == '__main__':
    # print(image2base64('7.png'))
    paths = [f'{i}.png' for i in range(1, 8)]
    base64s = [image2base64(i) for i in paths]

    write_base64(dict(zip([f'img{i}' for i in range(1, 8)], base64s)))
