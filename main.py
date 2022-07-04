import matplotlib.pyplot as plt
import numpy as np

data = []
nums = 11
for i in range(nums):
    # print(d, d + 3)
    sub_data = np.random.randint(1, 5, nums)
    data.append(sub_data)

print(data)
x = [i for i in range(1, nums + 1)]  # 确定柱状图数量,可以认为是x方向刻度
# y = [5, 7, 9, 10, 3, 6, 12, 2, 14, 8, 11, 16, 14, 13, 8]
# ty = []
# for i, v in enumerate(y):
#     ty.append((v, i))

# ty.sort(key=lambda a: a[0])
# pos = [0 for i in range(nums)]
#
# for i, v in enumerate(ty):
#     pos[v[1]] = i

color = ['#3b829d', '#c5bcd5', '#ebdbe0', '#129a2f', '#f1b066', '#7ebcd1', '#e9a390', '#2b9759', '#a2b324', '#d0ba1f',
         '#e3bd1c']

color_11 = ['#a04c47', '#007c49', '#9fb516', '#d8ca28', '#005e88', '#d5d804', '#47a11f', '#007070', '#de9d59',
            '#de9785', '#485599']

color_15 = ['#4fa227', '#8dbf79', '#beb3cf', '#a0c01a', '#e48112', '#e1281e', '#74b7c9', '#deb616', '#c79cae',
            '#d5ba13', '#c7ba16', '#e0a016', '#e96a10', '#cb5f65', '#c1cde3']

# color_use = [color[x] for x in pos]
# color_use_15 = [color_15[x] for x in pos]
# color_use_11 = [color_11[x] for x in pos]

color_sorted = ['#2b9759', '#129a2f', '#a2b324', '#d0ba1f', '#e3bd1c', '#f1b066', '#e9a390', '#ebdbe0', '#c5bcd5',
                '#7ebcd1', '#3b829d']

color_sorted_11 = ['#de9785', '#de9d59', '#d8ca28', '#d5d804', '#9fb516', '#47a11f', '#007c49', '#007070', '#005e88',
                   '#485599', '#a04c47']
color_sorted_15 = ['#e1281e', '#e96a10', '#e48112', '#e0a016', '#deb616', '#d5ba13', '#c7ba16', '#a0c01a', '#4fa227',
                   '#8dbf79', '#74b7c9', '#c1cde3', '#beb3cf', '#c79cae', '#cb5f65']

# color_sorted_use = [color_sorted[x] for x in pos]
# color_sorted_use_15 = [color_sorted_15[x] for x in pos]
# color_sorted_use_11 = [color_sorted_11[x] for x in pos]

plt.xticks(x)  # 绘制x刻度标签
# plt.bar(x, y, color=color)  # 绘制y刻度标签

# 设置网格刻度
# plt.grid(True, linestyle=':', color='r', alpha=0.6)


# plt.bar(
#     x,
#     y,
#     color=color_use_15
# )
plt.stackplot(x, data, colors=color_11)

plt.savefig('_unsorted_stack_11.png', transparent=True)  # 设置背景透明
# plt.bar(
#     x,
#     y,
#     color=color_sorted_use_15
# )
plt.stackplot(x, data, colors=color_sorted_11)
plt.savefig('_sorted_stack_11.png', transparent=True)  # 设置背景透明
plt.show()
