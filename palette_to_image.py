import argparse
import os
import PIL.Image as Image
import sys
from color_palette import *

sys.path.append(".")
sys.path.append("..")


def save(palette, file_name, image_dir="palette_images", repeat=True, color_block_width=100):
    os.makedirs(image_dir, exist_ok=True)
    color_palette = ColorPalette(auto_fetched=False, colors=palette)
    # color_block_width = 100
    if repeat:
        bulked_up = color_palette.bulk_up(width=color_block_width)
    else:
        bulked_up = color_palette.bulk_up(
            width=color_block_width, repeat=False)
    image_name = '%s.png' % (file_name)
    path = os.path.join(image_dir, image_name)
    if os.path.exists(path):
        os.remove(path)
    Image.fromarray(bulked_up).save(path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--hexes', nargs="+", required=True)
    parser.add_argument('--filename', required=False, default="palette")

    args = parser.parse_args()
    # hexes: "aa3820 e7a557 d9d6ac 0c8fa7 255a58 373a3c 5b6057 6e9d95 e5d7af ebbb6d"
    hex_list = ["#%s" % hex for hex in args.hexes]

    save(hex_list, args.filename)
