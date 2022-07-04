from sko.SA import SA_TSP
from sko.PSO import PSO_TSP
from sko.IA import IA_TSP
from sko.GA import GA_TSP
from WOA import WhaleOptimization
from colormap import ColorMap
from colormath.color_conversions import *
from colormath.color_objects import *
from colormath.color_diff import delta_e_cie1976
from colormath.color_diff import delta_e_cie2000
import numpy as np
from palette_to_image import save
import os
import cv2

from sko.ACA import ACA_TSP
from geo_sorter_helper import *
import time
from csv_reader import CsvReader
from sps_evaluation import SpsEvaluation
from itertools import permutations


class OrderSorter:
    def __init__(self, palette, name, solve_mode=SolverMode.PSO, palette_kind=ColorMapKind.Discrete):
        self.palette = palette  # input a hex list
        self.name = name  # palette name
        self.num_points = len(palette)
        self.distance_matrix = []
        self.palette_lab = []  # lab list
        self.step = None  # sampling step
        self.solve_mode = solve_mode  # sorting function(SA)
        self.samples = []  # sample points
        self.samples_hex = []  # sample points hex
        self.samples_sorted = []  # sorted sampling points
        self.samples_hex_sorted = []
        self.palette_sorted = []  # sorted hex palette

        self.initial_global_order = 0
        self.final_global_order = 0
        self.initial_local_order = 0
        self.final_local_order = 0
        self.target = 0  # 优化目标的最终解
        self.start = 0  # 优化目标的初始值
        self.palette_kind = palette_kind  # continuous or discrete colormap
        self.elapsed_time = None  # sorting time

        for color in self.palette:
            rgb = sRGBColor.new_from_rgb_hex(color)
            lab = convert_color(rgb, LabColor)
            self.palette_lab.append(lab)

    # 对连续的colormap进行采样
    def continuous_sampling(self, step=20):
        self.step = step
        left, right = 0, self.num_points - 1
        while left < right:
            self.samples.append(left)
            self.samples.append(right)
            left += step
            right -= step
        self.samples.append(int((left + right) / 2))
        self.samples.sort()  # 按顺序采样
        # 计算初始order
        self.initial_global_order = self.calculate_global_order(self.samples)
        self.initial_local_order = self.calculate_local_order(self.samples)

        self.samples_hex = [self.palette[i] for i in self.samples]

    # 对离散的colormap进行采样
    def discrete_sampling(self, step=100):
        self.step = step
        for i in range(0, self.num_points, step):
            self.samples.append(i)
        # 初始order
        self.initial_local_order = self.calculate_local_order(self.samples)
        self.initial_global_order = self.calculate_global_order(self.samples)

        self.samples_hex = [self.palette[i] for i in self.samples]

    # 计算距离矩阵
    def calculate_distance_matrix(self):
        for i, c1 in enumerate(self.palette_lab):
            sub_matrix = []
            for j, c2 in enumerate(self.palette_lab):
                dis = (self.num_points * delta_e_cie1976(c1, c2) if i != j else 0)
                sub_matrix.append(dis)
            self.distance_matrix.append(sub_matrix)

    def calculate_global_order(self, palette):
        global_speed = np.inf
        for ix, x in enumerate(palette):
            for iy, y in enumerate(palette):
                if x != y:
                    global_speed = min(global_speed, self.distance_matrix[x][y] / abs(ix - iy))

        return global_speed

    def calculate_local_order(self, palette):
        local_speed = np.inf
        n = len(palette)
        for i in range(1, n):
            local_speed = min(local_speed, self.distance_matrix[palette[i - 1]][palette[i]])
        return local_speed

    def func(self, routine):
        global_speed = np.inf
        for i, x in enumerate(routine):
            for j, y in enumerate(routine):
                if x != y:
                    global_speed = min(global_speed,
                                       self.distance_matrix[self.samples[x]][self.samples[y]] / abs(i - j))

        local_speed = 0
        n = len(routine)
        total_local_speed = 0

        for i in range(1, n):
            dv = self.distance_matrix[self.samples[routine[i - 1]]][self.samples[routine[i]]]
            local_speed = max(local_speed, dv)
            total_local_speed += dv

        return - global_speed + 5 * local_speed + total_local_speed / n
        # return -global_speed + 5*local_speed
        # return total_local_speed / n

    def standard_sort(self, loop=3):
        start_time = time.time()

        T_max, T_min = 500, 10
        iteration_per_temperature = 200 * len(self.samples)
        best_points = range(len(self.samples))  # 初始解
        self.start = self.func(best_points)  # 优化目标的初始值
        while loop > 0:
            solver = SA_TSP(func=self.func, x0=best_points, T_max=T_max, T_min=T_min,
                            L=iteration_per_temperature)
            best_points, self.target = solver.run()
            loop -= 1

        end_time = time.time()
        self.elapsed_time = end_time - start_time
        return best_points.tolist()

    def sort(self, loop=1):
        print(self.solve_mode)
        start_time = time.time()
        best_points = range(len(self.samples))  # 初始解
        self.start = self.func(best_points)  # 优化目标的初始值

        if self.solve_mode == SolverMode.SA:
            T_max, T_min = 500, 80
            iteration_per_temperature = 100 * len(self.samples)
            # cooling factor = 0.9 in SKO

            solver = SA_TSP(func=self.func, x0=best_points, T_max=T_max, T_min=T_min, L=iteration_per_temperature)
            best_points, best_global_legend_based_speed = solver.run()

        elif self.solve_mode == SolverMode.GA:
            size_pop = round(8 * len(self.samples))
            max_iter = 30 * len(self.samples)
            solver = GA_TSP(func=self.func, n_dim=len(self.samples), size_pop=size_pop, max_iter=max_iter, prob_mut=1)
            best_points, self.target = solver.run()

        elif self.solve_mode == SolverMode.PSO:
            size_pop = round(7.5 * len(self.samples))
            max_iter = 30 * len(self.samples)
            solver = PSO_TSP(func=self.func, n_dim=len(self.samples), size_pop=size_pop, max_iter=max_iter, w=0.8,
                             c1=0.1, c2=0.1)
            best_points, self.target = solver.run()
        elif self.solve_mode == SolverMode.IA:
            solver = IA_TSP(func=self.func, n_dim=len(self.samples), size_pop=50, max_iter=200, prob_mut=0.001, T=0.7,
                            alpha=0.95)
            best_points, self.target = solver.run()
        elif self.solve_mode == SolverMode.ACO50:
            ant_count = 5
            max_iter = 30 * len(self.samples)
            aca = ACA_TSP(func=self.func, n_dim=len(self.samples), size_pop=ant_count,
                          max_iter=max_iter, distance_matrix=self.distance_matrix)

            best_points, self.target = aca.run()
        elif self.solve_mode == SolverMode.ACO100:
            ant_count = 100
            max_iter = 30 * len(self.samples)
            aca = ACA_TSP(func=self.func, n_dim=len(self.samples), size_pop=ant_count,
                          max_iter=max_iter, distance_matrix=self.distance_matrix)

            best_points, self.target = aca.run()
        elif self.solve_mode == SolverMode.ACO20:
            ant_count = 20
            max_iter = 30 * len(self.samples)
            aca = ACA_TSP(func=self.func, n_dim=len(self.samples), size_pop=ant_count,
                          max_iter=max_iter, distance_matrix=self.distance_matrix)

            best_points, self.target = aca.run()
        else:
            raise Exception('sort error')

        # 计算时间
        end_time = time.time()
        self.elapsed_time = end_time - start_time

        return best_points.tolist()

    def solve(self, best_points):
        # best_points is a list
        self.samples_sorted = [self.samples[x] for x in best_points]
        # 亮到暗
        lightness_costs = self.get_lightness_cost()
        if lightness_costs[self.samples_sorted[0]] > lightness_costs[self.samples_sorted[-1]]:
            self.samples_sorted.reverse()

        # 计算final order
        self.final_local_order = self.calculate_local_order(self.samples_sorted)
        self.final_global_order = self.calculate_global_order(self.samples_sorted)

        self.samples_hex_sorted = [self.palette[x] for x in self.samples_sorted]

    def interpolate(self):
        last = None
        cnt = 0
        for p in range(self.num_points):
            if p in self.samples:
                self.palette_sorted.append(self.palette[self.samples_sorted[cnt]])
                last = (p, self.palette_lab[self.samples_sorted[cnt]])
                cnt += 1
            else:
                nxt_pos = self.samples[self.samples.index(last[0]) + 1]  # 下一个应该放置控制点的位置
                nxt = (nxt_pos, self.palette_lab[self.samples_sorted[cnt]])  # cnt已经+1
                c1 = np.array(last[1].get_value_tuple())  # 如果用rgb color space
                c2 = np.array(nxt[1].get_value_tuple())
                color = ((c2 - c1) * (p - last[0]) / (nxt[0] - last[0])) + c1
                lab = LabColor(color[0], color[1], color[2])
                rgb = convert_color(lab, sRGBColor)
                r, g, b = rgb.get_value_tuple()
                rgb = sRGBColor(min(1.0, r), min(1.0, g), min(1.0, b), False)

                self.palette_sorted.append(rgb.get_rgb_hex())

    def save_image(self, image_dir):
        suffix = ''
        if self.solve_mode == SolverMode.SA:
            suffix += '_SA'
        elif self.solve_mode == SolverMode.GA:
            suffix += '_GA'
        elif self.solve_mode == SolverMode.PSO:
            suffix += '_PSO'
        elif self.solve_mode == SolverMode.IA:
            suffix += '_IA'
        elif self.solve_mode == SolverMode.WOA:
            suffix += '_WOA'
        else:
            raise Exception('Error')

        # 保存排序前后的控制点
        # if self.samples_hex:
        #     img_name = self.name + '_' + str(self.initial_global_order)
        #     save(self.samples_hex, img_name, image_dir=image_dir, repeat=True, color_block_width=100)
        if self.samples_hex_sorted:
            img_name = self.name + '_sorted_' + str(self.final_global_order)
            save(self.samples_hex_sorted, img_name, image_dir=image_dir, repeat=True, color_block_width=100)
        # 保存连续colormap插值后的结果
        if self.palette_kind == ColorMapKind.Continuous:
            img_name = self.name + suffix  # + '_step' + str(self.step)
            save(self.palette_sorted, img_name, image_dir=image_dir, repeat=False, color_block_width=10)

    def get_lightness_cost(self):
        lightness_costs = []
        for lab in self.palette_lab:
            L, A, B = lab.get_value_tuple()
            lightness_costs.append(1.0 - (L / 100))
        return lightness_costs
