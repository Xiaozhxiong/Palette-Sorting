import os
import cv2
from colormath.color_conversions import *
from colormath.color_objects import *
from OrderSorter import OrderSorter
from palette_to_image import save

if __name__ == '__main__':
    image_path = 'D:\\GitDemo\\DCCW-dataset\\KHTP\\KHTP-interpolation1-jitter10\\KHTP-interpolation1-jitter10-image\\KHTP-p23-1-sorted.png'
    image = cv2.imread(image_path)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    palette = []
    for i in range(0, image_rgb.shape[1], image_rgb.shape[0]):
        r, g, b = image_rgb[0][i]
        rgb = sRGBColor(r, g, b, True)
        palette.append(rgb.get_rgb_hex())

    print(palette)
    # sorter = OrderSorter(palette=palette, name='_')
    # sorter.calculate_distance_matrix()
    # step = 1
    # sorter.discrete_sampling(step=step)
    # best_points = sorter.sort()  # 采样点取值
    # sorter.solve(best_points)  # 排序
    # palette_sorted = [palette[x] for x in sorter.samples_sorted]
    # f = os.path.split(image_path)[-1]
    # save_dir = os.path.split(image_path)[0]
    # name = f[:f.index('.')]
    # print(name)
    # save(palette_sorted, name + '-sorted(1-1-1)', image_dir=save_dir, repeat=True,
    #      color_block_width=100)
