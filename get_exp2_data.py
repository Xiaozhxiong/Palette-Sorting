import os
import cv2
import numpy as np
from OrderSorter import OrderSorter
from geo_sorter_helper import *
from palette_to_image import save
from colormath.color_conversions import *
from colormath.color_objects import *
from colormath.color_objects import *
from similarity_measurer import SimilarityMeasurer
from color_palette import ColorPalette
from geo_sorter_helper import *
from palette_to_image import save


def get_palette(image_path):
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    p = []
    for i in range(0, img.shape[1], img.shape[0]):
        r, g, b = img[0][i]
        rgb = sRGBColor(r, g, b, True)
        p.append(rgb.get_rgb_hex())
    return p


def cal_sim(palette, palette_name, cal_dir):
    s_dir = 'PerceptualStudy/experiment_2/unsorted'
    sim_list = []  # 保存相似度和对于的图片名称
    pa = ColorPalette(auto_fetched=False, colors=palette)
    for f in os.listdir(cal_dir):
        # 来自同一图片的调色板
        f_path = os.path.join(cal_dir, f)
        tp = get_palette(f_path)
        print(tp)
        pb = ColorPalette(auto_fetched=False, colors=tp)
        similarity_measurer = SimilarityMeasurer(pa, pb, LabDistanceMode.CIEDE2000)
        sim, _, _ = similarity_measurer.standard_measure()
        sim_list.append((sim, f, tp))
    # 排序
    sim_list.sort(key=lambda t: t[0])
    # 选择第1个和最后1个保存
    print(palette_name, sim_list[1][1], sim_list[-1][1])
    save(palette, palette_name, image_dir=s_dir, repeat=True, color_block_width=100)
    save(sim_list[1][2], palette_name + '-0', image_dir=s_dir, repeat=True, color_block_width=100)
    save(sim_list[9][2], palette_name + '-1', image_dir=s_dir, repeat=True, color_block_width=100)
    return sim_list[1][2], sim_list[9][2]


if __name__ == '__main__':
    k_list = [5]
    palettes = []
    names = []
    for k in k_list:
        for p in range(10):
            if p != 3:
                continue
            solve_dir = 'PerceptualStudy/experiment_2/exp2/k{}-p{}'.format(k, p)  # 查找数据所在位置
            aim_dir = 'PerceptualStudy/inputs/k{}/k{}-p{}.png'.format(k, k, p)
            aim_palette = get_palette(aim_dir)
            print(aim_palette)
            x, y = cal_sim(aim_palette, 'k{}-p{}'.format(k, p), solve_dir)
            palettes.append([aim_palette, x, y])
            names.append('k{}-p{}'.format(k, p))

    print('find finished.')
    dst_dir = 'PerceptualStudy/experiment_2/k5-p3'
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
    for (i, palette) in enumerate(palettes):
        print(palettes)
        total = palette[0] + palette[1] + palette[2]  # 合并排序
        sorter = OrderSorter(palette=total, name=' ')
        sorter.calculate_distance_matrix()
        step = 1
        sorter.discrete_sampling(step=step)
        best_points = sorter.sort()  # 采样点取值
        sorter.solve(best_points)  # 排序
        # 分开
        split_palette = [[], [], []]
        n = int(len(total) / 3)
        for x in sorter.samples_sorted:
            if x < n:
                split_palette[0].append(palette[0][x])
            elif n <= x < 2 * n:
                split_palette[1].append(palette[1][x - n])
            else:
                split_palette[2].append(palette[2][x - 2 * n])
        save([total[x] for x in sorter.samples_sorted], 'total-ours(1-5-20)', image_dir=dst_dir, repeat=True,
             color_block_width=100)
        for j, sp in enumerate(split_palette):
            name = names[i]
            if j == 1:
                name += '-0'
            elif j == 2:
                name += '-1'
            save(sp, name + '-ours(1-5-20)', image_dir=dst_dir, repeat=True, color_block_width=100)

    # src_dir = 'PerceptualStudy/experiment_2/unsorted'
    # for file in os.listdir(src_dir):
    #     name = file[:file.index('.')]
    #     print(name)
    #     file_path = os.path.join(src_dir, file)
    #     tp = get_palette(file_path)
    #     # 排序
    #     sorter = OrderSorter(palette=tp, name=name)
    #     sorter.calculate_distance_matrix()
    #     step = 1
    #     sorter.discrete_sampling(step=step)
    #     best_points = sorter.sort()  # 采样点取值
    #     sorter.solve(best_points)  # 排序
    #     save([tp[x] for x in sorter.samples_sorted], name + '-ours', image_dir=dst_dir,
    #          repeat=True, color_block_width=100)
