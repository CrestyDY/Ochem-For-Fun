import my_database
import formatted_database


def quick_sort_nested(ls):
    if len(ls) <= 1:
        return ls

    # Separate lists where index 1 has the string '<0'
    string_less_than_zero = [x for x in ls if isinstance(x[1], str) and x[1] == '<0']

    # Separate numeric values and non-'<0' strings
    numeric_values = [x for x in ls if isinstance(x[1], (int, float))]
    other_strings = [x for x in ls if isinstance(x[1], str) and x[1] != '<0']

    # Quicksort the numeric values
    if len(numeric_values) <= 1:
        return string_less_than_zero + numeric_values + other_strings

    mid = numeric_values[len(numeric_values) // 2][1]

    left = [x for x in numeric_values if x[1] < mid]
    middle = [x for x in numeric_values if x[1] == mid]
    right = [x for x in numeric_values if x[1] > mid]

    # Combine the sorted sections
    return string_less_than_zero + quick_sort_nested(left) + middle + quick_sort_nested(right) + other_strings


ls = my_database.final_data
sorted_ls = quick_sort_nested(ls)
for i in range(len(sorted_ls)):
    sorted_ls[i][1] = str(sorted_ls[i][1])
    sorted_ls[i][2] = str(sorted_ls[i][2])

"""with open("output.txt", "w") as f:
    for i in range(len(sorted_ls)):
        print(formatted_database.x.format(sorted_ls[i][0],sorted_ls[i][1],sorted_ls[i][2],sorted_ls[i][3]), file=f)"""



