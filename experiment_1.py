from csv_reader import CsvReader
from sps_evaluation import SpsEvaluation
from OrderSorter import OrderSorter
from geo_sorter_helper import *
from colormath.color_diff import delta_e_cie1976
from colormath.color_diff import delta_e_cie2000

if __name__ == '__main__':
    k = 10
    kind = 'G1+L5+AvgLocal+{}'.format('PSO')
    solve_mode = SolverMode.PSO

    csv_reader = CsvReader('Datasets/FM100P/FM100P-k{}-csv'.format(k))
    # 记录global order的变换
    order_file_path = 'Results/FM100P/FM100P-k{}/Global_Order_Change({})WB.csv'.format(k, kind)
    order_file = open(order_file_path, 'a')
    id_file_path = 'Results/FM100P/FM100P-k{}/Color_IdList({})WB.csv'.format(k, kind)
    id_file = open(id_file_path, 'a')
    target_file_path = 'Results/FM100P/FM100P-k{}/Target_Change({})WB.csv'.format(k, kind)
    target_file = open(target_file_path, 'a')
    print(csv_reader.palette_num)
    X_gt, X_sorted = [], []  #
    elapsed_times = []  # 记录每个palette排序用时
    right = 0  # 正确的
    sorted_equal_gt = 0  # global 相等的
    nod = 0
    total_time = 0
    for idx, p in enumerate(csv_reader.palette_hex):
        # 进度
        if idx % 10 == 0 and idx > 0:
            print(" %d / %d " % (idx, csv_reader.palette_num))

        print(csv_reader.file_names[idx] + ',', end='', file=order_file)

        X_gt.append(sorted(csv_reader.id_list[idx]))  # 标准答案的结果颜色序号
        sorter = OrderSorter(palette=p, name=csv_reader.file_names[idx], solve_mode=solve_mode,
                             palette_kind=ColorMapKind.Discrete)

        sorter.calculate_distance_matrix()
        step = 1
        sorter.discrete_sampling(step=step)
        best_points = sorter.sort()  # 采样点取值
        sorter.solve(best_points)
        sorter.save_image('Results/FM100P/FM100P-k{}/images({})WB'.format(k, kind))
        # print([csv_reader.id_list[idx][x] for x in sorter.samples_sorted])
        total_time += sorter.elapsed_time
        # 排序的输出
        X_sorted.append([csv_reader.id_list[idx][x] for x in sorter.samples_sorted])
        elapsed_times.append(sorter.elapsed_time)
        # 计算标准答案的global order
        gt_id = sorted(csv_reader.id_list[idx])
        # print(gt_id)
        gt_palette = []
        for c in gt_id:
            gt_palette.append(p[csv_reader.id_list[idx].index(c)])

        sorter_gt = OrderSorter(palette=gt_palette, name=csv_reader.file_names[idx] + '_gt', solve_mode=solve_mode,
                                palette_kind=ColorMapKind.Discrete)

        sorter_gt.calculate_distance_matrix()
        sorter_gt.discrete_sampling(step)
        target_gt = sorter_gt.func(range(len(sorter_gt.samples)))
        # sorter_gt.save_image('Results/FM100P/FM100P-k20/GT')
        # 保存结果
        flag = 0  # 是否和gt一样
        if X_gt[-1] == X_sorted[-1]:
            flag = 1
            right += 1
        elif X_gt[-1] == X_sorted[-1][::-1]:
            flag = -1
        else:
            flag = 0
        if flag == -1:  # 正确
            nod += 1
        if sorter.final_global_order == sorter_gt.initial_global_order:
            sorted_equal_gt += 1

        # 保存global order的变化
        print(str(sorter.initial_global_order) + ',' + str(
            sorter.final_global_order) + ',' + str(sorter_gt.initial_global_order) + ',' + str(flag), file=order_file)
        # 颜色序号对比
        print(str(X_sorted[-1]) + ',' + str(X_gt[-1]), file=id_file)
        # 优化目标的变化记录
        print(str(sorter.start) + ',' + str(sorter.target) + ',' + str(target_gt), file=target_file)
        # 结果展示
    print(f'right number = {right} ,reverse = {nod} , global order equal number = {sorted_equal_gt} ,'
          f' avg_time = {total_time / csv_reader.palette_num}')

    order_file.close()
    id_file.close()
    target_file.close()

    # 计算评价指标
    # evaluator = SpsEvaluation('PSO', X_gt, X_sorted, csv_reader.palette_num, elapsed_times,
    #                           csv_dir='Results/FM100P/FM100P-k10')
    # evaluator.evaluation()
    # evaluator.save_result()
