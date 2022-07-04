import os
import math
import numpy as np
import shutil
import cv2
from colormath.color_conversions import *
from colormath.color_objects import *
from sklearn.manifold import TSNE
import json
from similarity_measurer import SimilarityMeasurer
from color_palette import ColorPalette
from geo_sorter_helper import *
from OrderSorter import OrderSorter
from palette_to_image import save

if __name__ == '__main__':
    # 随机得到展示的数据
    # numbers = 50
    # k_list = [5, 10, 15, 20, 25, 30]
    # jitters = [0, 5, 10, 15]
    # for k in k_list:
    #     replaces = [0, math.ceil(k / 10)]
    #     target_dir = 'Datasets/WedData/k{}'.format(k)
    #     if not os.path.exists(target_dir):
    #         os.makedirs(target_dir)
    #     for i in range(numbers):
    #         j = jitters[np.random.randint(0, len(jitters))]
    #         r = replaces[np.random.randint(0, 2)]
    #         sub_dir = 'Datasets/LHSP/LHSP-k{}-jitter{}-replacement{}/retrieval-palettes-images'.format(k, j, r)
    #         image_list = os.listdir(sub_dir)
    #         src_image = image_list[np.random.randint(0, len(image_list))]
    #         dst_image = ('k{}-p{}' + os.path.splitext(src_image)[-1]).format(k, i)
    #         print(os.path.join(sub_dir, src_image))
    #         shutil.copyfile(os.path.join(sub_dir, src_image), os.path.join(target_dir, dst_image))

    k_list = [x for x in range(5, 16, 1)]
    # tsne_results = []
    json_path = 'Datasets/WedData/'
    # 存每个palette的颜色
    palette_color = {}  # 未排序
    palette_color_sorted = {}  # 排序
    if not os.path.exists(json_path):
        os.makedirs(json_path)
    all_palettes = []
    all_names = []
    for k in k_list:
        print('k=', k)
        base_dir = 'Datasets/WedData/images/k{}'.format(k)
        save_dir = 'Datasets/WedData/images-sorted/k{}'.format(k)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        palettes = []
        # palettes_sorted = []
        lab_lists = []
        names = []
        # cnt = 6  # 每个长度计算6个就行
        for img in os.listdir(base_dir):
            name = img[:img.index('.')]
            names.append(name)
            all_names.append(name)
            palette_path = os.path.join(base_dir, img)
            image = cv2.imread(palette_path)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            # print(image_rgb.shape)
            palette = []
            lab_list = []
            for i in range(0, image_rgb.shape[1], image_rgb.shape[0]):
                r, g, b = image_rgb[0][i]
                rgb = sRGBColor(r, g, b, True)
                lab = convert_color(rgb, LabColor)
                palette.append(rgb.get_rgb_hex())
                lab_list.extend(list(lab.get_value_tuple()))

            # 对于长度不够的进行扩充 在计算总体时
            # for i in range(k, 15):
            #     lab_list.extend([100, 0, 0])

            palettes.append(palette)
            lab_lists.append(lab_list)  #
            palette_color[name] = palette
            all_palettes.append(lab_list)  #

            # 排序
            sorter = OrderSorter(palette=palette, name='_')
            sorter.calculate_distance_matrix()
            step = 1
            sorter.discrete_sampling(step=step)
            best_points = sorter.sort()  # 采样点取值
            sorter.solve(best_points)  # 排序
            palette_sorted = [palette[x] for x in sorter.samples_sorted]
            palette_color_sorted[name] = palette_sorted
            save(palette_sorted, name + '-sorted', image_dir=save_dir, repeat=True,
                 color_block_width=100)
            # palettes_sorted.append(palette_sorted)

            # cnt -= 1
            # if cnt <= 0:
            #     break

        # ========================分长度计算 TSNE 保存json
        # data = np.array(lab_lists)
        # tsne = TSNE(n_components=2)
        # result = tsne.fit_transform(data.reshape(data.shape[0], -1))
        # # tsne_results.append(result)
        # json_text = {}
        # for i in range(len(palettes)):
        #     json_text[names[i]] = {'pointX': result[i][0].item(), 'pointY': result[i][1].item()}
        # print(json_text)
        # json_data = json.dumps(json_text, indent=4)
        #
        # file = os.path.join(json_path, 'k{}.json'.format(k))
        # with open(file, 'w') as f:
        #     f.write(json_data)

        # ======================================= 计算相似度
        # num = len(palettes)
        # similarity_list = {}
        # for i in range(num):
        #     sub_list = []
        #     pa = ColorPalette(auto_fetched=False, colors=palettes[i])
        #     for j in range(num):
        #         pb = ColorPalette(auto_fetched=False, colors=palettes[j])
        #         similarity_measurer = SimilarityMeasurer(pa, pb, LabDistanceMode.CIEDE2000, improved=True)
        #         sim, _ = similarity_measurer.measure()
        #         sub_list.append({"id": names[j], "similarity": sim["DynamicClosestColorWarping"]})
        #     similarity_list[names[i]] = sub_list
        #     json_path = 'Datasets/WedData/similarity'
        #     if not os.path.exists(json_path):
        #         os.makedirs(json_path)
        #     json_data = json.dumps(similarity_list, indent=4)
        #     file = os.path.join(json_path, 'k{}.json'.format(k))
        #     with open(file, 'w') as f:
        #         f.write(json_data)

    # =========== 保存palette 的颜色信息
    json_data = json.dumps(palette_color_sorted, indent=4)
    file = os.path.join(json_path, 'palette_color_sorted.json')
    with open(file, 'w') as f:
        f.write(json_data)

    # ========================合并所有长度计算 TSNE 保存json
    # print(all_palettes)
    # all_data = np.array(all_palettes)
    # print(all_data.shape)
    # all_tsne = TSNE(n_components=2)
    # result = all_tsne.fit_transform(all_data.reshape(all_data.shape[0], -1))
    # # tsne_results.append(result)
    # json_text = {}
    # for i in range(len(all_palettes)):
    #     json_text[all_names[i]] = {'pointX': result[i][0].item(), 'pointY': result[i][1].item()}
    # print(json_text)
    # json_data = json.dumps(json_text, indent=4)
    #
    # file = os.path.join(json_path, 'all_palettes.json')
    # with open(file, 'w') as f:
    #     f.write(json_data)
