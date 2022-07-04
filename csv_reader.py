import csv
import os
from geo_sorter_helper import DataKind
import numpy as np


class CsvReader:
    def __init__(self, directory, data_kind=DataKind.FM100P):
        self.directory = directory
        self.data_kind = data_kind
        self.file_names = []  # 目录下所有文件名
        self.palette_hex = []
        self.palette_num = 0
        self.id_list = []  # 每种颜色的编号
        self.palette_len = 0
        self.read()

    def read(self):
        # 读取目录下所有文件
        print(self.directory)
        for file in os.listdir(self.directory):
            path = os.path.join(self.directory, file)
            if not os.path.exists(path):
                raise Exception(f'{path} does not exist')

            name = file[:file.index('.')]
            # print(name)a
            sub_palette = []
            ids = []
            with open(path, 'r') as f:
                if self.data_kind == DataKind.FM100P:
                    for line in f.readlines():
                        line = line.strip('\n')
                        idc, color = line.split('\t')
                        sub_palette.append(color)
                        ids.append(int(idc))

                elif self.data_kind == DataKind.KHTP:
                    num = 0
                    for line in f.readlines():
                        num += 1
                        line = line.strip('\n')
                        if num % 2 == 0:
                            sub_palette.extend(line.split('\t'))
                        else:
                            ids.extend(list(map(lambda x: int(x), line.split('\t'))))

            self.palette_hex.append(sub_palette)
            self.id_list.append(ids)

            self.palette_num += 1
            self.file_names.append(name)

        self.palette_len = np.array(self.palette_hex).shape[1]
        print(np.array(self.palette_hex).shape)


if __name__ == '__main__':
    reader = CsvReader('Datasets/KHTP/KHTP-interpolation0-jitter0-csv', data_kind=DataKind.KHTP)
    print(reader.file_names)
    print(np.array(reader.palette_hex).shape)
    print(np.array(reader.id_list).shape)
