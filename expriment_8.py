import os
import cv2
from palette_to_image import save
from OrderSorter import OrderSorter
from colormath.color_conversions import *
from colormath.color_objects import *
from similarity_measurer import SimilarityMeasurer
from color_palette import ColorPalette
from geo_sorter_helper import *
import shutil


def get_hex_palette(p_path):
    hex_palette = []
    img = cv2.imread(p_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    for i in range(0, img.shape[1], img.shape[0]):
        r, g, b = img[0][i]
        rgb = sRGBColor(r, g, b, True)
        hex_palette.append(rgb.get_rgb_hex())
    return hex_palette


def get_ColorPalette(p):
    return ColorPalette(auto_fetched=False, colors=p)


def cal_similarity(pa, pb):
    similarity_measurer = SimilarityMeasurer(pa, pb, LabDistanceMode.CIEDE2000, need_sort=False)
    sim, _, _ = similarity_measurer.standard_measure()
    return sim


# 选择一些调色板，排序前后的计算相似度
if __name__ == '__main__':
    unsort_dir = 'sims/imgs'
    imgs_sorted = os.path.join('sims', 'imgs_sorted')
    if not os.path.exists(imgs_sorted):
        os.makedirs(imgs_sorted)
    sorted_dir = imgs_sorted
    dst_dir = 'sims'
    # palette_selected = get_hex_palette('sims/imgs/122-photo_radiofreebarton.png')
    # color_palette_selected = get_ColorPalette(palette_selected)
    # 先计算未排序前的相似度
    # sims_unsort = []
    for file in os.listdir(unsort_dir):
        name = file[:file.index('.')]
        palette_path = os.path.join(unsort_dir, file)
        palette = get_hex_palette(palette_path)
        print(name, ':')
        print(palette)
        # color_palette = get_ColorPalette(palette)
        # sub_sim = cal_similarity(color_palette_selected, color_palette)
        # sims_unsort.append((sub_sim, name))

        # 排序
        sorter = OrderSorter(palette=palette, name='_')
        sorter.calculate_distance_matrix()
        step = 1
        sorter.discrete_sampling(step=step)
        best_points = sorter.sort()  # 采样点取值
        sorter.solve(best_points)  # 排序
        palette_sorted = [palette[x] for x in sorter.samples_sorted]
        save(palette_sorted, name + '-sorted', image_dir=imgs_sorted, repeat=True,
             color_block_width=100)

    # sims_unsort.sort(key=lambda x: x[0])
    # unsort_dst = os.path.join(dst_dir, 'unsort')
    # if not os.path.exists(unsort_dst):
    #     os.makedirs(unsort_dst)
    # cnt = 0
    # for sim, name in sims_unsort:
    #     file_name = str(cnt) + '_' + name + '.png'
    #     src_file = os.path.join(unsort_dir, name + '.png')
    #     dst_file = os.path.join(unsort_dst, file_name)
    #     print(src_file)
    #     print(dst_file)
    #     shutil.copyfile(src_file, dst_file)
    #     cnt += 1

    # 排序后计算相似度
    # palette_selected = get_hex_palette('sims/imgs_sorted/122-photo_radiofreebarton-sorted.png') # 选择的调色板
    # sims_sorted = []
    for file in os.listdir(sorted_dir):
        name = file[:file.index('.')]
        palette_path = os.path.join(sorted_dir, file)
        palette = get_hex_palette(palette_path)
        print(name)
        print(palette)
    #     color_palette = get_ColorPalette(palette)
    # sub_sim = cal_similarity(color_palette_selected, color_palette)
    # sims_sorted.append((sub_sim, name))
    # sims_sorted.sort(key=lambda x: x[0])

    # sorted_dst = os.path.join(dst_dir, 'sorted')
    # if not os.path.exists(sorted_dst):
    #     os.makedirs(sorted_dst)
    # cnt = 0
    # for sim, name in sims_sorted:
    #     file_name = str(cnt) + '_' + name + '.png'
    #     src_file = os.path.join(sorted_dir, name + '.png')
    #     dst_file = os.path.join(sorted_dst, file_name)
    #     shutil.copyfile(src_file, dst_file)
    #     cnt += 1
