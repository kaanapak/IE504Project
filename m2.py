list_ratios = []

# for ratio_int in range(4, 9):
#     ratio_1 = ratio_int / 10
#     for ratio_int2 in range(4, 9):
#         ratio_2 = ratio_int2 / 10
#         for ratio_int3 in range(4, 9):
#             ratio_3 = ratio_int3 / 10
#             for ratio_int4 in range(4, 9):
#                 ratio_4 = ratio_int4 / 10
#                 for ratio_int5 in range(4, 9):
#                     ratio_5 = ratio_int5 / 10
#                     list_ratios.append([ratio_1,ratio_2,ratio_3,ratio_4,ratio_5])

for ratio_int in range(0, 6):
    ratio_1 = ratio_int / 10
    for ratio_int2 in range(0, 6):
        ratio_2 = ratio_int2 / 10
        for ratio_int3 in range(0, 6):
            ratio_3 = ratio_int3 / 10
            for ratio_int4 in range(0, 6):
                ratio_4 = ratio_int4 / 10
                for ratio_int5 in range(0, 6):
                    ratio_5 = ratio_int5 / 10
                    list_ratios.append( [ratio_1, ratio_2, ratio_3, ratio_3, ratio_3, ratio_3, ratio_3, ratio_3, ratio_3, ratio_3, ratio_3,ratio_3, ratio_4, ratio_5])


import matplotlib.pyplot as plt
#x = [1,2,3]
print(len(list_ratios))
y = list_ratios
#plt.xlabel("X-axis")
plt.ylabel("Y-axis")
plt.title("A test graph")
#plt.plot(y[0])
for i in y:
    plt.plot(i)
plt.legend()
plt.show()