def find_all(substring: str, string: str):
    """Yields starting positions of all occurrences of a substring in a string"""
    pos = string.find(substring)
    while pos != -1:
        yield pos
        pos = string.find(substring, pos+1)


def find_last(subseq, sequence, n_matches: int) -> list:
    """Finds starting positions of the last n matches of the pattern in the sequence
    :param n_matches: number of last matches to find"""
    len_p = len(subseq)
    k = len(sequence) - len_p
    match_pos = []
    while n_matches > 0 and k >= 0:
        if sequence[k: k + len_p] == subseq:
            match_pos.append(k)
            n_matches -= 1
        k -= 1
    return match_pos
