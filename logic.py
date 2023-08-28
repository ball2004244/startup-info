from typing import List

#* Description: find index of 1st element in lst2 that not in lst1
#! Time complexity: O(n)
#! Space complexity: O(n)
def first_diff_idx(lst1: List[str], lst2: List[str]) -> int:
    # if 2 lists are the same
    if lst1 == lst2:
        return -1
    
    overlap = []
    i, j = 0, 0
    while i < len(lst1) and j < len(lst2):
        if lst1[i] == lst2[j]:
            overlap.append(lst1[i])
            i += 1
            j += 1
        elif lst1[i] < lst2[j]:
            i += 1
        else:
            j += 1
    
    if not overlap:
        return 0
    
    return lst2.index(overlap[-1]) + 1

if __name__ == '__main__':
    import pickle
    
    # save prev_lst to prev_lst.pkl
    prev_file = 'prev_lst.pkl'
    try:
        with open(prev_file, 'rb') as f:
            prev_lst = pickle.load(f)
    except FileNotFoundError:
        prev_lst = []

    cur_lst = ['b', 'c', 'd', 'e', 'f']
    
    # save cur_lst to prev_lst.pkl
    with open(prev_file, 'wb') as f:
        pickle.dump(cur_lst, f)
        
    idx = first_diff_idx(prev_lst, cur_lst)    
    print(idx)