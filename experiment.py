from OrderSorter import OrderSorter
from geo_sorter_helper import *
from csv_reader import CsvReader
from sps_evaluation import SpsEvaluation
from pps_evaluation import PpsEvaluation
import os
import csv
from palette_to_image import save
from single_palette_sorter import SinglePaletteSorter
from color_palette import ColorPalette


class Experiment:
    def __init__(self, k=10, i=0, j=0, solve_mode=SolverMode.PSO, data_kind=DataKind.FM100P,
                 palette_kind=ColorMapKind.Discrete, sort_kind=SortKind.SPS):
        self.k = k
        self.solve_mode = solve_mode

        if data_kind == DataKind.FM100P:
            # FM100P
            kind = 'FM100P'
            # self.data_path = 'Datasets/{}/{}-k{}-csv'.format(kind, kind, k)
            self.data_path = 'D:\GitDemo\DCCW-dataset\FM100P\FM100P-k{}/FM100P-k{}-csv'.format(k, k)
            self.result_path = 'Results/{}/{}-k{}'.format(kind, kind, k)
            # 对于35和40的数据,分成5部分分开算
            # self.data_path = 'Datasets/{}/{}-k{}-csv/part{}-{}'.format(kind, kind, k, 80, 99)
            # self.result_path = 'Results/{}/{}-k{}/part{}-{}'.format(kind, kind, k, 80, 99)

        else:
            # KHTP
            kind = 'KHTP'
            self.data_path = 'Datasets/{}/{}-interpolation{}-jitter{}-csv'.format(kind, kind, i, j)
            self.result_path = 'Results/{}/{}-interpolation{}-jitter{}'.format(kind, kind, i, j)

        self.X_gt = []
        self.X_sorted = []
        self.elapsed_times = []
        self.single_time = 0
        self.right_count = 0
        self.palette_kind = palette_kind
        self.data_kind = data_kind
        self.sort_kind = sort_kind
        self.data = self.read()

    def read(self):
        reader = CsvReader(self.data_path, self.data_kind)
        return reader

    def run(self):
        # test_num = 10
        for idx, palette in enumerate(self.data.palette_hex):
            # print(idx)
            if self.data.file_names[idx] != 'KHTP-p45':
                continue

            if self.sort_kind == SortKind.SPS:
                sorted_points = self.sps(palette, self.data.file_names[idx], self.solve_mode, ColorMapKind.Discrete)
                self.X_sorted.append([self.data.id_list[idx][x] for x in sorted_points])
                self.X_gt.append(sorted(self.data.id_list[idx]))

                # =========输出不正确的
                if self.X_sorted[-1] != self.X_gt[-1] and self.X_sorted[-1][::-1] != self.X_gt[-1]:
                    print(self.data.file_names[idx])
                    print(self.X_sorted[-1])
                # ==========保存图片============

                # image_path = os.path.join(self.result_path, 'images(PSO_G1_L1_A1)')
                # image_name = self.data.file_names[idx]
                # # save(palette, image_name, image_dir=image_path, repeat=True, color_block_width=100)
                # image_name = self.data.file_names[idx] + "_sorted"
                # save([palette[x] for x in sorted_points], image_name, image_dir=image_path, repeat=True,
                #      color_block_width=100)

            elif self.sort_kind == SortKind.PPS:
                self.pps(palette, self.data.file_names[idx], self.solve_mode, ColorMapKind.Discrete, idx)

    def sps(self, palette, palette_name, solve_mode, palette_kind):
        sorter = OrderSorter(palette=palette, name=palette_name, solve_mode=solve_mode, palette_kind=palette_kind)
        sorter.calculate_distance_matrix()
        step = 1
        sorter.discrete_sampling(step=step)
        best_points = sorter.sort()  # 采样点取值
        sorter.solve(best_points)  # 排序
        # image_path = os.path.join(self.result_path, 'images_sorted')
        # sorter.save_image(image_path)
        # 排序结果(颜色id)
        self.elapsed_times.append(sorter.elapsed_time)  # 排序时间
        return sorter.samples_sorted

    def pps(self, palette, palette_name, solve_mode, palette_kind, idx):
        n = len(palette) // 2
        # 改变合并方式
        # color_palette = ColorPalette(auto_fetched=False, colors=palette)
        # sps = SinglePaletteSorter(palette=color_palette)
        # sorted_points, _ = sps.sort(spsm=SinglePaletteSortMode.LKH_CIEDE2000)
        # init_palette = [palette[x] for x in sorted_points]
        # pos = [0 for i in range(n * 2)]
        # for i, p in enumerate(sorted_points):
        #     pos[i] = p
        sorted_points = self.sps(palette, palette_name, solve_mode, palette_kind)
        # 原来的
        palette_1 = [x for x in sorted_points if x < n]
        palette_2 = [x for x in sorted_points if x >= n]

        # 交叉合并后
        # palette_1 = [pos[x] for x in sorted_points if pos[x] < n]
        # palette_2 = [pos[x] for x in sorted_points if pos[x] >= n]
        # 排序后仍合并一个,前面是第一个后面是第二个
        self.X_sorted.append(
            [self.data.id_list[idx][x] for x in palette_1] + [self.data.id_list[idx][x] for x in palette_2])
        self.X_gt.append(sorted(self.data.id_list[idx][:n]) + sorted(self.data.id_list[idx][n:]))
        # ==========保存图片============
        image_path = os.path.join(self.result_path, 'images(test_ours_p)')
        # image_name = palette_name + "_0"
        # save(palette[:n], image_name, image_dir=image_path, repeat=True, color_block_width=100)
        # image_name = palette_name + "_1"
        # save(palette[n:], image_name, image_dir=image_path, repeat=True, color_block_width=100)
        # 保存排序后分开的palette
        image_name = palette_name + "_0_sorted(010)"
        save([palette[x] for x in palette_1], image_name, image_dir=image_path, repeat=True, color_block_width=100)
        image_name = palette_name + "_1_sorted(010)"
        save([palette[x] for x in palette_2], image_name, image_dir=image_path, repeat=True, color_block_width=100)
        # # 合并的palette
        # image_name = palette_name + "_sorted"
        # save([palette[x] for x in sorted_points], image_name, image_dir=image_path, repeat=True, color_block_width=100)

    def save_sort_result(self, file_name='sort_result'):

        if self.sort_kind == SortKind.SPS:
            file_name += '_sps'
        elif self.sort_kind == SortKind.PPS:
            file_name += '_pps'

        if self.solve_mode == SolverMode.SA:
            file_name += '(SA)'
        elif self.solve_mode == SolverMode.PSO:
            file_name += '(PSO_G1_L1_A1)'
        elif self.solve_mode == SolverMode.GA:
            file_name += '(GA)'
        elif self.solve_mode == SolverMode.ACO50:
            file_name += '(ACO50)'
        elif self.solve_mode == SolverMode.ACO100:
            file_name += '(ACO100)'
        elif self.solve_mode == SolverMode.ACO20:
            file_name += '(ACO20)'
        print(file_name)
        path = os.path.join(self.result_path, file_name + '.csv')
        with open(path, 'w', newline='') as file:
            csv_writer = csv.writer(file)
            for x, y in zip(self.X_sorted, self.X_gt):
                csv_writer.writerow(x)
                csv_writer.writerow(y)
        print('avg sorting time(s) = {}'.format(sum(self.elapsed_times) / self.data.palette_num))

    def evaluate(self):
        evaluator = SpsEvaluation(self.solve_mode, self.X_gt, self.X_sorted, self.data.palette_num, self.elapsed_times)
        result = evaluator.evaluation()
        file_name = 'eval_result'
        if self.solve_mode == SolverMode.SA:
            file_name += '(SA).txt'
        elif self.solve_mode == SolverMode.PSO:
            file_name += '(PSO_G1_L1_A1).txt'
        elif self.solve_mode == SolverMode.GA:
            file_name += '(GA).txt'
        elif self.solve_mode == SolverMode.ACO50:
            file_name += '(ACO50).txt'
        elif self.solve_mode == SolverMode.ACO100:
            file_name += '(ACO100).txt'
        elif self.solve_mode == SolverMode.ACO20:
            file_name += '(ACO20).txt'
        path = os.path.join(self.result_path, file_name)
        with open(path, 'w') as file:
            print(result, file=file)
        for x in evaluator.get_not_correct():
            print(x, self.data.file_names[x])

    def pps_eval(self):
        eva = PpsEvaluation(self.solve_mode, self.X_gt, self.X_sorted, self.data.palette_num, self.elapsed_times)
        result = eva.cal()
        name = 'eval_result(Ours-test).txt'
        path = os.path.join(self.result_path, name)
        with open(path, 'w') as file:
            print(result, file=file)
        return result


if __name__ == "__main__":
    # ==========SPS
    # for k in range(30, 31, 5):
    #     experiment = Experiment(k=k, solve_mode=SolverMode.PSO, data_kind=DataKind.FM100P, sort_kind=SortKind.SPS)
    #     experiment.run()
        # experiment.save_sort_result()
        # experiment.evaluate()

    # ============= PPS实验

    p_experiment = Experiment(i=0, j=0, solve_mode=SolverMode.PSO, data_kind=DataKind.KHTP, sort_kind=SortKind.PPS)
    p_experiment.run()
