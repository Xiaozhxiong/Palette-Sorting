import os
import numpy as np
import math
import shutil
import cv2
from colormath.color_conversions import *
from colormath.color_objects import *
from OrderSorter import OrderSorter
from multiple_palettes_sorter import MultiplePalettesSorter
from single_palette_sorter import SinglePaletteSorter
from color_palettes import ColorPalettes
from geo_sorter_helper import *
from color_palette import ColorPalette
from palette_to_image import save

if __name__ == '__main__':
    # k=5,10,15
    # 生成输入图片
    # nums_palette = 10
    # jitters = [0, 5, 10, 15]
    # for k in [5, 10, 15]:
    #     replaces = [0, math.ceil(k / 10)]
    #     target_dir = 'PerceptualStudy/inputs/k{}'.format(k)
    #     if not os.path.exists(target_dir):
    #         os.makedirs(target_dir)
    #     for p in range(nums_palette):
    #         # 随机选择一个长度为k的palette
    #         j = jitters[np.random.randint(0, len(jitters))]
    #         r = replaces[np.random.randint(0, 2)]
    #         sub_dir = 'Datasets/LHSP/LHSP-k{}-jitter{}-replacement{}/retrieval-palettes-images'.format(k, j, r)
    #         image_list = os.listdir(sub_dir)
    #         src_image = image_list[np.random.randint(0, len(image_list))]
    #         dst_image = ('k{}-p{}' + os.path.splitext(src_image)[-1]).format(k, p)
    #         print(os.path.join(sub_dir, src_image))
    #         shutil.copyfile(os.path.join(sub_dir, src_image), os.path.join(target_dir, dst_image))

    # 排序保存
    for k in [5, 10, 15]:
        src_dir = 'PerceptualStudy/inputs/k{}'.format(k)
        dst_dir = 'PerceptualStudy/outputs/k{}'.format(k)
        for f in os.listdir(src_dir):
            img_path = os.path.join(src_dir, f)
            img = cv2.imread(img_path)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            p = []
            for point in img[0]:
                rgb = sRGBColor(point[0], point[1], point[2], True)
                p.append(rgb.get_rgb_hex())
            palette = [p[x] for x in range(0, len(p), img.shape[0])]
            print(palette)
            palette_name = f[:f.index('.png')]
            for kind in range(3):
                if kind != 2:
                    continue
                if kind == 0:
                    image_path = os.path.join(dst_dir, 'ours(151)')
                    sorter = OrderSorter(palette=palette, name=palette_name)
                    sorter.calculate_distance_matrix()
                    step = 1
                    sorter.discrete_sampling(step=step)
                    best_points = sorter.sort()  # 采样点取值
                    sorter.solve(best_points)  # 排序
                    # save([palette[x] for x in sorter.samples_sorted], palette_name + '-ours', image_dir=image_path,
                    #      repeat=True, color_block_width=100)
                elif kind == 1:
                    image_path = os.path.join(dst_dir, 'sps')
                    color_palette = ColorPalette(auto_fetched=False, colors=palette)
                    sps = SinglePaletteSorter(palette=color_palette)
                    sorted_points, etime = sps.sort(spsm=SinglePaletteSortMode.LKH_CIEDE2000)
                    # save([palette[x] for x in sorted_points], palette_name + '-sps', image_dir=image_path,
                    #      repeat=True, color_block_width=100)
                else:
                    image_path = os.path.join(dst_dir, 'hsv')
                    color_palette = ColorPalette(auto_fetched=False, colors=palette)
                    sps = SinglePaletteSorter(palette=color_palette)
                    sorted_points, etime = sps.sort(spsm=SinglePaletteSortMode.HSV)
                    # save([palette[x] for x in sorted_points], palette_name + '-hsv', image_dir=image_path,
                    #      repeat=True, color_block_width=100)
