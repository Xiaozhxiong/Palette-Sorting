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
from palette_to_image import save
import random

if __name__ == "__main__":
    nums = 50
    k_list = range(5, 16, 1)
    # 生成随机的palette
    for k in k_list:
        jitters = [0, 5, 10, 15]
        replaces = [0, math.ceil(k / 10)]
        target_dir = 'Datasets/WedData/images/k{}'.format(k)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        for i in range(nums):
            j = jitters[np.random.randint(0, len(jitters))]
            if k in [5, 10, 15]:
                r = replaces[np.random.randint(0, 2)]
                sub_dir = 'Datasets/LHSP/LHSP-k{}-jitter{}-replacement{}/retrieval-palettes-images'.format(k, j, r)
                image_list = os.listdir(sub_dir)
                src_image = image_list[np.random.randint(0, len(image_list))]
                dst_image = ('k{}-p{}' + os.path.splitext(src_image)[-1]).format(k, i)
                print(os.path.join(sub_dir, src_image))
                shutil.copyfile(os.path.join(sub_dir, src_image), os.path.join(target_dir, dst_image))
            else:
                mk = [20, 25, 30]
                tk = mk[np.random.randint(0, len(mk))]
                r_list = [0, math.ceil(tk / 10)]
                r = r_list[np.random.randint(0, 2)]
                sub_dir = 'Datasets/LHSP/LHSP-k{}-jitter{}-replacement{}/retrieval-palettes-images'.format(tk, j, r)
                image_list = os.listdir(sub_dir)
                src_image = image_list[np.random.randint(0, len(image_list))]
                img_path = os.path.join(sub_dir, src_image)
                image = cv2.imread(img_path)
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                palette = []
                for x in range(0, image_rgb.shape[1], image_rgb.shape[0]):
                    r, g, b = image_rgb[0][x]
                    rgb = sRGBColor(r, g, b, True)
                    palette.append(rgb.get_rgb_hex())

                rand_list = random.sample(range(len(palette)), k)
                sub_palette = []
                for x in rand_list:
                    sub_palette.append(palette[x])
                image_name = 'k{}-p{}'.format(k, i)
                save(sub_palette, image_name, image_dir=target_dir, repeat=True, color_block_width=100)
