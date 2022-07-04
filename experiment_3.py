import os
from similarity_measurer import SimilarityMeasurer
from color_palette import ColorPalette
from geo_sorter_helper import *
import numpy as np
import csv


class LHSPReader:
    def __init__(self, k, j, r):
        self.data_path = 'Datasets/LHSP/LHSP-k{}-jitter{}-replacement{}'.format(k, j, r)
        self.data = {}

    def read_files(self):
        self.data['query'] = {}
        self.data['query']['name'] = []
        self.data['query']['length'] = []
        self.data['query']['palette'] = []
        self.data['retrieval'] = {}
        self.data['retrieval']['name'] = []
        self.data['retrieval']['length'] = []
        self.data['retrieval']['palette'] = []
        query_nums = 0
        retrieval_nums = 0
        for file in os.listdir(self.data_path):
            path = os.path.join(self.data_path, file)
            if os.path.isfile(path) and os.path.splitext(path)[1] == '.csv':
                with open(path, 'r') as f:
                    for line in f.readlines():
                        line = line.strip('\n')
                        name, num, tmp_palette = line.split('\t', 2)
                        palette = tmp_palette.split('\t')
                        if file == 'query-palettes.csv':
                            query_nums += 1
                            csv_type = 'query'
                        elif file == 'retrieval-palettes.csv':
                            retrieval_nums += 1
                            csv_type = 'retrieval'
                        else:
                            raise Exception('error')
                        self.data[csv_type]['name'].append(name)
                        self.data[csv_type]['length'].append(int(num))
                        self.data[csv_type]['palette'].append(palette)

        print('finish reading {} , query_nums={} ,retrieval_nums={}'.format(self.data_path, query_nums, retrieval_nums))
        print(self.data['query']['name'])
        # print(self.data['retrieval']['name'])
        return self.data, query_nums, retrieval_nums


class SimMeasureComparer:
    def __init__(self, k=5, j=0, r=0):
        self.data, self.query_nums, self.retrieval_nums = LHSPReader(k, j, r).read_files()
        self.result_path = 'Results/LHSP/LHSP-k{}-jitter{}-replacement{}'.format(k, j, r)
        self.correct_nums = []
        self.right_nums = []
        self.original_similarity = []
        self.improved_similarity = []
        self.mAPs = []  # 0:原始的 1:改进后
        if not os.path.exists(self.result_path):
            os.makedirs(self.result_path)

    def compare(self):
        # 返回每种方法改进前后对于当前数据集的准确率
        self.original_similarity = self.similarity_measure()
        print(self.correct_nums)
        print('original finished')
        print(self.original_similarity)
        # self.improved_similarity = self.similarity_measure(improved=True)
        self.mAPs.append(self.cal(self.original_similarity))
        # self.mAPs.append(self.cal(self.improved_similarity))
        print(self.mAPs)
        file = 'result.csv'
        file_path = os.path.join(self.result_path, file)
        with open(file_path, 'w', newline='') as f:
            csv_writer = csv.writer(f)
            csv_writer.writerow(list(self.mAPs[0].keys()))
            for i in range(len(self.mAPs)):
                line = []
                for mAP in self.mAPs[i].values():
                    line.append(mAP)
                    csv_writer.writerow(line)

    def similarity_measure(self, improved=False):
        ranks_data = []  # 按测量方法记录每个的相似度(query_palette,measure_tag,[(similarity,index)])
        for i in range(self.query_nums):
            rank_data = {}
            correct = 0
            for j in range(self.retrieval_nums):
                correct += (self.data['query']['name'][i] == self.data['retrieval']['name'][j])
                target_data = {}
                query_palette = ColorPalette(auto_fetched=False, colors=self.data['query']['palette'][i])
                retrieval_palette = ColorPalette(auto_fetched=False, colors=self.data['retrieval']['palette'][i])
                if improved:
                    similarity_measurer = SimilarityMeasurer(query_palette, retrieval_palette,
                                                             LabDistanceMode.CIEDE2000, improved=True)
                else:
                    similarity_measurer = SimilarityMeasurer(query_palette, retrieval_palette,
                                                             LabDistanceMode.CIEDE2000)

                target_data['similarities'], _, target_data['elapsed_time'] = similarity_measurer.measure(
                    include_elapsed_time=True)
                for tag, similarity in target_data['similarities'].items():
                    if tag in rank_data.keys():
                        rank_data[tag].append((similarity, j))
                    else:
                        rank_data[tag] = [(similarity, j)]

            for key in rank_data.keys():
                rank_data[key].sort(key=lambda x: x[0])
            ranks_data.append(rank_data)
            # print(correct)
            if not improved:
                self.correct_nums.append(correct)
        return ranks_data

    def cal(self, similarity_list):
        # 返回每种方法对应的改进前后的mAP
        target_data = {}
        for i in range(self.query_nums):
            print(i, '===================')
            for key in similarity_list[i].keys():
                right = 0
                for j in range(self.retrieval_nums):
                    if similarity_list[i][key][j][0] > similarity_list[i][key][0][0]:
                        break
                    idx = similarity_list[i][key][j][1]
                    right += (self.data['query']['name'][i] == self.data['retrieval']['name'][idx])
                if key in target_data.keys():
                    target_data[key].append(1.0 * right / self.correct_nums[i])
                else:
                    target_data[key] = [1.0 * right / self.correct_nums[i]]

        mAP = {}
        for tag, similarity_list in target_data.items():
            mAP[tag] = np.mean(similarity_list)

        return mAP


if __name__ == '__main__':
    comparer = SimMeasureComparer(30, 15, 3)
    # comparer.similarity_measure(improved=True)
    comparer.compare()
