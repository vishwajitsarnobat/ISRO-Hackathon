from get_time import get_time_difference
from paths import file_paths


def get_differences(list_of_paths):

    list_ = []

    for i in range(1, len(list_of_paths)):
        time_diff = get_time_difference(list_of_paths[i - 1], list_of_paths[i])
        time_diff = round(time_diff, 2)
        list_.append(time_diff)
         
    for i in range(1, len(list_)):
        list_[i] += list_[i - 1]

    for j in range(len(list_)):
        list_[j] = round(list_[j], 2)

    return list_
