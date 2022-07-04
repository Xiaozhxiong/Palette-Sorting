from multiple_palettes_sorter import MultiplePalettesSorter
from single_palette_sorter import SinglePaletteSorter
from color_palettes import ColorPalettes
from geo_sorter_helper import *
from color_palette import ColorPalette
from csv_reader import CsvReader
from sps_evaluation import SpsEvaluation
import os
from pps_evaluation import PpsEvaluation
from experiment import Experiment
from palette_to_image import save

'''
SPS:
对比实验，需要计算LHK,LAB,HSV
'''


class ColorMapSorter:
    def __init__(self, data_path, data_kind, result_path, solve_mode=SolverMode.LKH,
                 palette_kind=ColorMapKind.Discrete, sort_kind=SortKind.SPS):
        self.solve_mode = solve_mode
        self.palette_kind = palette_kind
        self.sort_kind = sort_kind
        self.X_gt = []
        self.X_sorted = []
        self.elapsed_times = []
        self.data_path = data_path
        self.data_kind = data_kind
        self.result_path = result_path
        self.data = self.read()

        if not os.path.exists(self.result_path):
            os.makedirs(self.result_path)

    def read(self):
        reader = CsvReader(self.data_path, self.data_kind)
        return reader

    def sort(self):
        # sps
        if self.sort_kind == SortKind.SPS:
            for idx, palette in enumerate(self.data.palette_hex):
                color_palette = ColorPalette(auto_fetched=False, colors=palette)
                sps = SinglePaletteSorter(palette=color_palette)
                if self.solve_mode == SolverMode.LKH:
                    sorted_points, etime = sps.sort(spsm=SinglePaletteSortMode.LKH_CIEDE2000)
                elif self.solve_mode == SolverMode.LAB:
                    sorted_points, etime = sps.sort(spsm=SinglePaletteSortMode.Luminance)

                elif self.solve_mode == SolverMode.HSV:
                    sorted_points, etime = sps.sort(spsm=SinglePaletteSortMode.HSV)
                else:
                    sorted_points, etime = None, None
                self.X_sorted.append([self.data.id_list[idx][x] for x in sorted_points])
                self.X_gt.append(sorted(self.data.id_list[idx]))
                self.elapsed_times.append(etime)
                # 把不正确的挑出来
                if self.X_sorted[-1] != self.X_gt[-1] and self.X_sorted[-1][::-1] != self.X_gt[-1]:
                    print(self.data.file_names[idx])
                    save_path = os.path.join(self.result_path, 'WrongPalettes({})'.format('LAB'))
                    save([palette[x] for x in sorted_points], self.data.file_names[idx],
                         image_dir=save_path, repeat=True, color_block_width=100)

        elif self.sort_kind == SortKind.PPS:
            for idx, palette in enumerate(self.data.palette_hex):
                n = len(palette) // 2
                a = palette[:n]
                b = palette[n:]
                color_palette = ColorPalettes(
                    auto_fetched=False, color_palettes_list=[a, b], is_hex_list=True)
                pps = MultiplePalettesSorter(palettes=color_palette, palette_count=2,
                                             lab_distance_mode=LabDistanceMode.CIEDE2000)
                # LKH
                if self.solve_mode == SolverMode.PPS:
                    sorted_points, etime, merged_sorted_indices = pps.sort(
                        multiple_palette_sort_mode=MultiplePalettesSortMode.Merge_LKH)
                # BPS
                elif self.solve_mode == SolverMode.BPS:
                    sorted_points, etime, merged_sorted_indices = pps.sort(
                        multiple_palette_sort_mode=MultiplePalettesSortMode.BPS)
                # I-BPS
                elif self.solve_mode == SolverMode.I_BPS:
                    sorted_points, etime, merged_sorted_indices = pps.sort(
                        multiple_palette_sort_mode=MultiplePalettesSortMode.Improved_BPS)
                elif self.solve_mode == SolverMode.Order:
                    pass
                else:
                    sorted_points, etime = None, None

                self.X_sorted.append([self.data.id_list[idx][x] for x in sorted_points[0]] +
                                     [self.data.id_list[idx][x + n] for x in sorted_points[1]])
                self.X_gt.append(sorted(self.data.id_list[idx][:n]) + sorted(self.data.id_list[idx][n:]))
                self.elapsed_times.append(etime)
                # 保存图片
                save_path = os.path.join(self.result_path, 'images({})'.format('I-BPS'))
                save([palette[x] for x in sorted_points[0]], self.data.file_names[idx]+'-0',
                     image_dir=save_path, repeat=True, color_block_width=100)
                save([palette[x + n] for x in sorted_points[1]], self.data.file_names[idx]+'-1',
                     image_dir=save_path, repeat=True, color_block_width=100)


        else:
            raise Exception('solve mode error')

    def evaluate(self):
        if self.sort_kind == SortKind.SPS:
            eva = SpsEvaluation(self.solve_mode, self.X_gt, self.X_sorted, self.data.palette_num, self.elapsed_times)
            result = eva.evaluation()
        elif self.sort_kind == SortKind.PPS:
            eva = PpsEvaluation(self.solve_mode, self.X_gt, self.X_sorted, self.data.palette_num, self.elapsed_times)
            result = eva.cal()
        else:
            raise Exception('error')

        name = 'eval_result'
        if self.solve_mode == SolverMode.LKH:
            name += '(LKH).txt'
        elif self.solve_mode == SolverMode.LAB:
            name += '(LAB).txt'
        elif self.solve_mode == SolverMode.HSV:
            name += '(HSV).txt'
        elif self.solve_mode == SolverMode.PPS:
            name += '(PPS).txt'
        elif self.solve_mode == SolverMode.BPS:
            name += '(BPS).txt'
        elif self.solve_mode == SolverMode.I_BPS:
            name += '(I-BPS).txt'
        else:
            name += '.txt'
        path = os.path.join(self.result_path, name)
        with open(path, 'w') as file:
            print(result, file=file)
        return result


if __name__ == '__main__':
    # sps: LKH,LAB,HSV
    # k = 15
    # cs = ColorMapSorter(
    #     data_path='D:\GitDemo\DCCW-dataset\FM100P\FM100P-k{}\FM100P-k{}-csv'.format(k, k),
    #     # 'Datasets/FM100P/FM100P-k{}-csv'.format(k),
    #     data_kind=DataKind.FM100P,
    #     result_path='Results/FM100P/FM100P-k{}'.format(k),
    #     solve_mode=SolverMode.LAB,
    #     sort_kind=SortKind.SPS
    # )
    # cs.sort()

    # cs.evaluate()

    # ============== PPS 计算指标
    N_LD = 0
    N_LLIS = 0
    C_LD = 0
    C_LLCS = 0
    cnt = 0
    for i in range(0, 1):
        for j in range(0, 1, 5):
            # print(i, j)
            # cnt += 1
            # ========== others
            # cs = ColorMapSorter(
            #     data_path='Datasets/KHTP/KHTP-interpolation{}-jitter{}-csv'.format(i, j),
            #     data_kind=DataKind.KHTP,
            #     result_path='Results/KHTP/KHTP-interpolation{}-jitter{}'.format(i, j),
            #     solve_mode=SolverMode.I_BPS,
            #     sort_kind=SortKind.PPS
            # )
            # cs.sort()
            # res = cs.evaluate()

            # =============== Ours:
            ex = Experiment(i=i, j=j,
                            solve_mode=SolverMode.PSO,
                            data_kind=DataKind.KHTP,
                            sort_kind=SortKind.PPS)
            ex.run()
            # ex.save_sort_result()
            # res = ex.pps_eval()

            # N_LD += res['Naturalness_LD']
            # N_LLIS += res['Naturalness_LLIS']
            # C_LD += res['Concurrency_LD']
            # C_LLCS += res['Concurrency_LLCS']
            # print(res['Concurrency_LD'], res['Concurrency_LLCS'])

    print('N_LD = %.3f , N_LLIS = %.3f , C_LD = %.3f , C_LLCS = %.3f' % (
        N_LD / cnt, N_LLIS / cnt, C_LD / cnt, C_LLCS / cnt))
