import csv
import os
from geo_sorter_helper import *


def longest_increasing_subsequence(nums):
    n = len(nums)
    dp = []
    for i in range(n):
        dp.append(1)
        for j in range(i):
            if nums[i] > nums[j]:
                dp[i] = max(dp[i], dp[j] + 1)
    return max(dp)


def Lev_distance(a, b):
    # http://rosettacode.org/wiki/Levenshtein_distance#Python
    costs = []
    for j in range(len(b) + 1):
        costs.append(j)
    for i in range(1, len(a) + 1):
        costs[0] = i
        nw = i - 1
        for j in range(1, len(b) + 1):
            cj = min(1 + min(costs[j], costs[j - 1]),
                     nw if a[i - 1] == b[j - 1] else nw + 1)
            nw = costs[j]
            costs[j] = cj

    return costs[len(b)] / max(len(a), len(b))


class SpsEvaluation:
    def __init__(self, method, x_gt, x_sorted, nums, times, sort_kind=SortKind.SPS):
        self.method = method  # 使用的排序方法
        self.sequences_gt = x_gt  # 有序序列
        self.sequences_sorted = x_sorted  # 输出序列
        self.numbers = nums  # palette 数量
        self.times = times  # 记录time的list
        self.LD_list = []  # Levenshtein distance list
        self.LD = None
        self.LLIS_list = []  # length of the longest increasing subsequence
        self.LLIS = None
        self.SR = 0  # success rate
        self.ET = None  # elapsed time in seconds
        self.sort_kind = sort_kind
        self.num_parts = (1 if self.sort_kind == SortKind.SPS else 2)
        self.not_correct = []

    def calculate_success_rate(self):
        # Success rate is the success proportion among a number of tests,
        # and success means that a sorting method correctly arranged the palette colors.
        count = 0
        for i in range(self.numbers):
            if self.sequences_gt[i] == self.sequences_sorted[i] or self.sequences_sorted[i][::-1] == \
                    self.sequences_gt[i]:
                count += 1
            else:
                self.not_correct.append(i)
        print('count = %d ' % count)
        self.SR = 1.0 * count / self.numbers
        return self.SR

    def calculate_Levenshtein_Distance(self):
        for i in range(self.numbers):
            sa = self.sequences_sorted[i]
            sb = self.sequences_gt[i]
            if sa.index(min(sa)) > len(sa) * 0.5:
                sa = list(reversed(sa))
            dis = Lev_distance(sa, sb)
            self.LD_list.append(dis)

        self.LD = sum(self.LD_list) / self.numbers
        return self.LD

    def calculate_LLIS(self):
        # the longest subsequence length for the sorted elements
        for i in range(self.numbers):
            nums = self.sequences_sorted[i]
            n = len(nums)
            if nums.index(min(nums)) > len(nums) * 0.5:
                nums = list(reversed(nums))
            res = longest_increasing_subsequence(nums)
            self.LLIS_list.append(1.0 * res / n)

        self.LLIS = sum(self.LLIS_list) / self.numbers
        return self.LLIS

    def calculate_times(self):
        self.ET = sum(self.times) / self.numbers
        return self.ET

    def evaluation(self):
        result = {
            'method': self.method,
            'SR': self.calculate_success_rate(),
            'LD': self.calculate_Levenshtein_Distance(),
            'LLIS': self.calculate_LLIS(),
            'ET': self.calculate_times()
        }
        return result

    def get_not_correct(self):
        return self.not_correct


if __name__ == '__main__':
    X_s = [[1, 3, 2, 4, 6], [1, 2, 5, 6, 7]]
    X_ans = [[1, 2, 3, 4, 5], [1, 2, 5, 6, 7]]

    elapsed_times = [3445, 3454]
    evaluator = SpsEvaluation('Global', X_s, X_ans, 2, elapsed_times)
    print(evaluator.evaluation())
