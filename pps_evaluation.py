def levenshtein_distance(a, b):
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


def get_longest_increasing_subsequence_length(indices):
    LIS = []

    def insert(target):
        left, right = 0, len(LIS) - 1
        # Find the first index "left" which satisfies LIS[left] >= target
        while left <= right:
            mid = left + (right - left) // 2
            if LIS[mid] >= target:
                right = mid - 1
            else:
                left = mid + 1
        # If not found, append the target.
        if left == len(LIS):
            LIS.append(target);
        else:
            LIS[left] = target

    for num in indices:
        insert(num)

    return len(LIS) / len(indices)


def get_longest_common_subsequence_length(x, y):
    m = len(x)
    n = len(y)
    L = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if x[i - 1] == y[j - 1]:
                L[i][j] = L[i - 1][j - 1] + 1
            else:
                L[i][j] = max(L[i][j - 1], L[i - 1][j])

    return L[m][n] / min(len(x), len(y))


class PpsEvaluation:
    def __init__(self, method, x_gt, x_sorted, nums, times):
        self.method = method
        self.x_gt = x_gt
        self.x_sorted = x_sorted
        self.numbers = nums
        self.times = times

    def cal(self):
        print('pps_eval')
        n = len(self.x_sorted[0]) // 2
        naturalness_lv_distances = 0
        naturalness_lliss = 0
        concurrency_lv_distances = 0
        concurrency_lliss = 0
        for idx, mp in enumerate(self.x_sorted):
            p0 = mp[:n]
            p1 = mp[n:]
            initial_index = p0.index(0)
            p0_flatten = p0[initial_index:] + p0[:initial_index]
            initial_index = p1.index(0)
            p1_flatten = p1[initial_index:] + p1[:initial_index]
            p0_gt = self.x_gt[idx][:n]
            p1_gt = self.x_gt[idx][n:]
            concurrency_lv_distances += levenshtein_distance(p0_flatten, p1_flatten)
            concurrency_lliss += get_longest_common_subsequence_length(p0_flatten, p1_flatten)
            naturalness_lv_distances += (levenshtein_distance(p0_flatten, p0_gt) +
                                         levenshtein_distance(p1_flatten, p1_gt)) / 2
            naturalness_lliss += (get_longest_increasing_subsequence_length(p0_flatten) +
                                  get_longest_increasing_subsequence_length(p1_flatten)) / 2

        naturalness_levenshtein_distances = naturalness_lv_distances / self.numbers
        naturalness_LLISs = naturalness_lliss / self.numbers
        concurrency_levenshtein_distances = concurrency_lv_distances / self.numbers
        concurrency_LLCSs = concurrency_lliss / self.numbers

        return {
            'Naturalness_LD': naturalness_levenshtein_distances,
            'Naturalness_LLIS': naturalness_LLISs,
            'Concurrency_LD': concurrency_levenshtein_distances,
            'Concurrency_LLCS': concurrency_LLCSs
        }
