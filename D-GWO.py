import numpy as np
from sko.tools import func_transformer


class GWO:
    def __init__(self, func, n_dim=30, pop_size=50, max_iter=1000):
        super().__init__()
        self.func = func_transformer(func)
        self.n_dim = n_dim
        self.pop_size = pop_size
        self.max_iter = max_iter
        self.sols = self.init_solution()

    def init_solution(self):
        sols = np.random.rand(self.pop_size, self.n_dim)
        return np.argsort(sols, axis=1)

    def run(self):
        ranked_sols = self.rank_solutions(self.sols)
        sol_alpha, sol_beta, sol_delta = ranked_sols[0:3]
        for t in range(self.max_iter):
            print(t)
            new_sols = []
            for iw in range(self.pop_size):
                d_alpha, d_beta, d_delta = 0, 0, 0
                hd_alpha = self.get_hamming_distance(sol_alpha, self.sols[iw])
                if hd_alpha > 0:
                    d_alpha = np.random.randint(1, hd_alpha + 1)
                hd_beta = self.get_hamming_distance(sol_beta, self.sols[iw])
                if hd_beta > 0:
                    d_beta = np.random.randint(1, hd_beta + 1)
                hd_delta = self.get_hamming_distance(sol_delta, self.sols[iw])
                if hd_delta > 0:
                    d_delta = np.random.randint(1, hd_delta + 1)

                tmp_sols = []
                sub_sol = self.sols[iw]
                while d_alpha > 0:
                    sub_sol = self.two_opt(sub_sol)
                    d_alpha -= 1
                tmp_sols.append(sub_sol)

                sub_sol = self.sols[iw]
                while d_beta > 0:
                    sub_sol = self.two_opt(sub_sol)
                    d_beta -= 1
                tmp_sols.append(sub_sol)

                sub_sol = self.sols[iw]
                while d_delta > 0:
                    sub_sol = self.two_opt(sub_sol)
                    d_delta -= 1
                tmp_sols.append(sub_sol)

                new_sols.append(self.rank_solutions(tmp_sols)[0])

            self.sols = np.stack(new_sols)
            # update best wolves
            ranked_sols = self.rank_solutions(self.sols)
            sol_alpha, sol_beta, sol_delta = ranked_sols[0:3]

        return sol_alpha, self.func(sol_alpha.reshape(1, -1))

    def rank_solutions(self, sols):
        fitness = self.func(sols)
        sol_fitness = [(f, s) for f, s in zip(fitness, sols)]
        ranked_sols = list(sorted(sol_fitness, key=lambda x: x[0]))
        return [s[1] for s in ranked_sols]

    @staticmethod
    def get_hamming_distance(sa, sb):
        hd = 0
        for x, y in zip(sa, sb):
            hd += int(x != y)
        return hd

    def two_opt(self, sol):
        better_sol = sol
        better_fit = self.func(better_sol.reshape(1, -1))
        if better_sol.shape[0] < self.n_dim:
            print(better_sol)
        for i in range(self.n_dim - 1):
            for j in range(i + 1, self.n_dim):
                new_sol = np.hstack((better_sol[0:i], np.flipud(better_sol[i:j]), better_sol[j:]))
                new_fit = self.func(new_sol.reshape(1, -1))
                # print(new_sol)
                if new_fit < better_fit:
                    better_sol = new_sol
                    better_fit = new_fit

        return better_sol


if __name__ == '__main__':
    from scipy import spatial
    from sko.GA import GA_TSP

    num_points = 50
    points_coordinate = np.random.rand(num_points, 2)  # generate coordinate of points
    distance_matrix = spatial.distance.cdist(points_coordinate, points_coordinate, metric='euclidean')


    def cal_total_distance(routine):
        num, = routine.shape
        return sum([distance_matrix[routine[i % num], routine[(i + 1) % num]] for i in range(num)])


    gwo_tsp = GWO(func=cal_total_distance, n_dim=num_points, pop_size=30, max_iter=20)
    best_points, best_distance = gwo_tsp.run()
    print(best_points, best_distance)

    ga_tsp = GA_TSP(func=cal_total_distance, n_dim=num_points, size_pop=50, max_iter=1000, prob_mut=1)
    best_points, best_distance = ga_tsp.run()
    print(best_points, best_distance)
