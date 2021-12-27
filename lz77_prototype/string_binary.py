from functools import reduce

# Length of a character in bits (suggested 7 or 8)
_char_length = 7
__form = "{:0" + str(_char_length) + "b}"


def string_to_bits(s: str) -> str:
    """Converts string to sequence of ascii bits, e.g. 'cat' -> '01100011 01100001 01110100'"""
    return "".join([__form.format(ord(c)) for c in s])


def string_to_bit_arr(s: str) -> list:
    """Converts string to sequence of ascii bits, as list"""
    return reduce(lambda l1, l2: l1+l2, [bin_list(ord(c)) for c in s], [])


def bin_list(d: int) -> list:
    """Converts decimal number to binary - as list of integer bits, e.g. 39 -> [1, 0, 0, 1, 1, 1]"""
    return list(map(lambda x: int(x), list(__form.format(d))))


def bits_to_string(bits: str) -> str:
    """Converts sequence of ascii bits to the string, e.g. '01100011 01100001 01110100' -> 'cat'"""
    # Fix missing leading zeros
    n_missing_zeros = (_char_length - len(bits) % _char_length) % _char_length
    bits = '0' * n_missing_zeros + bits
    return "".join([chr(int(bits[i: i+_char_length], 2)) for i in range(0, len(bits), _char_length)])


def bit_arr_to_string(bits: list) -> str:
    """Converts sequence of ascii bits as list, to string"""
    return bits_to_string("".join(map(str, bits)))


def length_of_bits(s: str) -> int:
    """Returns length of a string converted to bits"""
    return _char_length * len(s)


if __name__ == '__main__':
    # msg = 'Call2JohnTellHim2LetAllMonkeysOutWipeHisDataOffSystem&TakeHisOldPhone'
    msg = 'cat'
    msg_b = string_to_bits(msg)
    print(msg_b)
    print(len(msg_b))
    msg_rec = bits_to_string(msg_b)
    print(msg_rec)