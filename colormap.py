import os
from posixpath import pardir
import numpy as np
from colormath.color_objects import *
from palette_to_image import save


class ColorMap:
    """
    默认从 colormap_input 目录下读取输入文件,
    一个palette一个文件
    """

    def __init__(self):
        self.file_name = []  # 记录所有输入的颜色文件的名称
        self.color = []  # 记录文件中保存的rgb float颜色信息
        self.rgb_hex_list = []  # 颜色的hex list

    def read_color_file(self):
        """
        读取所有输入 rgb 的浮点数表示
        """
        # 读取colormap下的所有文件
        dir = "colormap"
        for file in os.listdir(dir):
            self.file_name.append(self.get_name(file))
            file_path = os.path.join(dir, file)
            with open(file_path, "r") as f:
                palette = []
                for line in f.readlines():
                    line = line.strip('\n')
                    line = line.split(' ')
                    palette.append(line)
            self.color.append(palette)
        self.rgb_to_hex()

    def rgb_to_hex(self):
        for p in self.color:  # 遍历所有palette
            a_hex_list = []
            for c in p:  # 遍历一个palette的所有color
                rgb = sRGBColor(c[0], c[1], c[2], False)
                a_hex_list.append(rgb.get_rgb_hex())
            self.rgb_hex_list.append(a_hex_list)

    def get_name(self, file):
        name = file[:file.rindex('.')]
        return name


if __name__ == "__main__":
    colormap = ColorMap()
    colormap.read_color_file()
    # print(np.array(colormap.rgb_hex_list).shape)
    # print(colormap.file_name)
    count = 5
    for i in range(len(colormap.rgb_hex_list)):
        save(colormap.rgb_hex_list[i], colormap.file_name[i] + '_0', "continuous_colormaps", repeat=False,
             color_block_width=10)
        for j in range(count):
            palette = np.random.permutation(colormap.rgb_hex_list[i])
            save(palette, colormap.file_name[i] + '_' + str(j + 1), "continuous_colormaps", repeat=False,
                 color_block_width=10)
