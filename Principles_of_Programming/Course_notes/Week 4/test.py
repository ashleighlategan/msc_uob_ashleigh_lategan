def shift_right(in_list):
    out_list = [0] * len(in_list)
    for i in range(0, len(in_list)):
        out_list[i] = in_list[i-1]
    return out_list


print(shift_right([1,2,3,4]))