import os
import math
import numpy as np
import cv2
from colormath.color_conversions import *
from colormath.color_objects import *
from similarity_measurer import SimilarityMeasurer
from color_palette import ColorPalette
from geo_sorter_helper import *
from palette_to_image import save
import shutil


def get_palette(image_path):
    p = []
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    p = []
    for i in range(0, img.shape[1], img.shape[0]):
        r, g, b = img[0][i]
        rgb = sRGBColor(r, g, b,True)
        p.append(rgb.get_rgb_hex())
    return p


def cal_sim(palette, palette_name, tk, th, cal_dir):
    s_dir = 'PerceptualStudy/experiment_2/unsorted'
    sim_list = []  # 保存相似度和对于的图片名称
    pa = ColorPalette(auto_fetched=False, colors=palette)
    for f in os.listdir(cal_dir):
        pic_name = f[f.index('-') + 1:f.index('.')]
        # 来自同一图片的调色板
        if palette_name == pic_name:
            f_path = os.path.join(cal_dir, f)
            tp = get_palette(f_path)
            pb = ColorPalette(auto_fetched=False, colors=tp)
            similarity_measurer = SimilarityMeasurer(pa, pb, LabDistanceMode.CIEDE2000)
            sim, _, _ = similarity_measurer.standard_measure()
            # sim = sims[SimMeasureStrategy.DynamicClosestColorWarping]
            sim_list.append((sim, f, tp))
    # 排序
    sim_list.sort(key=lambda t: t[0])
    # 选择第1个和最后1个保存
    s_name = 'k{}-p{}'.format(tk, th)
    print(palette_name, sim_list[1][1], sim_list[-1][1])
    save(palette, s_name, image_dir=s_dir, repeat=True, color_block_width=100)
    save(sim_list[1][2], s_name + '-0', image_dir=s_dir, repeat=True, color_block_width=100)
    save(sim_list[-1][2], s_name + '-1', image_dir=s_dir, repeat=True, color_block_width=100)


if __name__ == '__main__':
    k_list = [5, 10, 15]
    base_dir = 'Datasets/LHSP/'
    for k in k_list:
        aim_dir = 'PerceptualStudy/inputs/k{}'.format(k)
        cnt = 0
        # 对应长度的所有palette
        for x in os.listdir(aim_dir):
            xPath = os.path.join(aim_dir, x)
            aimPalette = get_palette(xPath)
            aimName = ''
            print('=====>', x)
            flag = False
            # loc_dir = ''
            mv_dir = 'PerceptualStudy/experiment_2/exp2/k{}-p{}'.format(k, cnt)
            if not os.path.exists(mv_dir):
                os.makedirs(mv_dir)
            for j in [0, 5, 10, 15]:
                for r in [0, math.ceil(k / 10)]:
                    sub_dir = 'LHSP-k{}-jitter{}-replacement{}/retrieval-palettes-images'.format(k, j, r)
                    find_dir = os.path.join(base_dir, sub_dir)
                    for file in os.listdir(find_dir):
                        img_path = os.path.join(find_dir, file)
                        p_name = file[file.index('-') + 1:file.index('.')]
                        p = get_palette(img_path)
                        if p == aimPalette:
                            flag = True
                            # loc_dir = sub_dir
                            print(x, " : ", file, sub_dir)
                            aimName = p_name
                            # cal_sim(aimPalette, p_name, k, cnt, find_dir)
                            break
                    # 把来自统一图片的移动到一起
                    for file in os.listdir(find_dir):
                        p_name = file[file.index('-') + 1:file.index('.')]
                        if p_name == aimName:
                            src_img = os.path.join(find_dir, file)
                            shutil.copyfile(src_img, os.path.join(mv_dir, file))
                    if flag:
                        break
                if flag:
                    break
            cnt += 1
