def find_all(substring: str, string: str):
    """Yields starting positions of all occurrences of a substring in a string"""
    pos = string.find(substring)
    while pos != -1:
        yield pos
        pos = string.find(substring, pos+1)


def find_last(substring: str, string: str, n_matches: int):
    """Finds last <n_matches> occurrences of a substring in a string. Yields
    starting positions"""
    pos = string.rfind(substring)
    match_cnt = 0
    while pos != -1 and match_cnt < n_matches:
        yield pos
        pos = string.rfind(substring, 0, pos+len(substring)-1)
        match_cnt += 1

