"""
排序算法实现
用于：商店物品价格排序
"""

def merge_sort(items, key_func, reverse=False):
    """
    归并排序实现
    :param items: 待排序列表
    :param key_func: 获取比较值的函数 (例如 lambda x: x['price'])
    :param reverse: 是否降序
    :return: 新的已排序列表
    """
    if len(items) <= 1:
        return items

    mid = len(items) // 2
    left = merge_sort(items[:mid], key_func, reverse)
    right = merge_sort(items[mid:], key_func, reverse)

    return _merge(left, right, key_func, reverse)

def _merge(left, right, key_func, reverse):
    sorted_list = []
    i = j = 0

    while i < len(left) and j < len(right):
        val_left = key_func(left[i])
        val_right = key_func(right[j])

        if not reverse:
            if val_left <= val_right:
                sorted_list.append(left[i])
                i += 1
            else:
                sorted_list.append(right[j])
                j += 1
        else:
            if val_left >= val_right:
                sorted_list.append(left[i])
                i += 1
            else:
                sorted_list.append(right[j])
                j += 1

    sorted_list.extend(left[i:])
    sorted_list.extend(right[j:])
    return sorted_list