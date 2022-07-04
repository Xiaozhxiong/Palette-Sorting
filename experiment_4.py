from OrderSorter import OrderSorter
import os
import cv2
from colormath.color_conversions import *
from colormath.color_objects import *

if __name__ == '__main__':
    img_dir = 'Datasets/Continuous/interchange-imgs'
    for file in os.listdir(img_dir):
        print(file)
        file_name = file[:file.index('.')]
        path = os.path.join(img_dir, file)
        img = cv2.imread(path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        p = []
        # print(img.shape[0])
        for point in img[0]:
            rgb = sRGBColor(point[0], point[1], point[2], True)
            p.append(rgb.get_rgb_hex())
        palette = [p[x] for x in range(0, len(p), img.shape[0])]
        # print(palette)

        sorter = OrderSorter(palette=palette, name=file_name)
        sorter.calculate_distance_matrix()
        step = 1
        sorter.discrete_sampling(step=step)
        best_points = sorter.sort()  # 采样点取值
        sorter.solve(best_points)

