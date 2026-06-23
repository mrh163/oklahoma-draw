def add_lists(LL: list[list[int]]) -> list[int]:
    if len(LL) == 0:
        L = []
    elif len(LL) == 1:
        L = list(set(LL[0]))
    elif len(LL) == 2:
        x1 = set(LL[0])
        x2 = set(LL[1])
        L = list(x1.union(x2))
    else:
        L = add_lists([LL[0], add_lists(LL[1:])])

    return sorted(L)

def int_lists(LL: list[list[int]]) -> list[int]:
    if len(LL) == 0:
        raise Exception("Cannot take intersection of empty list of lists")
    elif len(LL) == 1:
        L = list(set(LL[0]))
    elif len(LL) == 2:
        x1 = set(LL[0])
        x2 = set(LL[1])
        L = list(x1.intersection(x2))
    else:
        L = int_lists([LL[0], int_lists(LL[1:])])

    return sorted(L)

def invert_list(L):
    return sorted(list(set(range(5)).difference(set(L))))

def cmp_lists(L1: list[int], L2: list[int]) -> int:
    L1 = sorted(L1, reverse=True)
    L2 = sorted(L2, reverse=True)
    for k in range(len(L1)):
        if k >= len(L2):
            raise Exception(f"Could not compare lists L1 = {L1} and L2 = {L2} because all elements in L2[:len(L1)] equal their counterparts of L1")
        elif L1[k] < L2[k]:
            return -1
        elif L1[k] > L2[k]:
            return 1
    if len(L2) > len(L1):
        raise Exception(f"Could not compare lists L1 = {L1} and L2 = {L2} because all elements in L1[:len(L2)] equal their counterparts of L2")
    return 0    
