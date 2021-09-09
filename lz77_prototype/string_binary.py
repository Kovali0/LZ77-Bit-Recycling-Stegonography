# Length of a character in bits (suggested 7 or 8)
_char_length = 8
__form = "{:0" + str(_char_length) + "b}"

def string_to_bits(s: str) -> str:
    """Converts string to sequence of ascii bits, e.g. 'cat' -> '01100011 01100001 01110100'"""
    return "".join([__form.format(ord(c)) for c in s])


def bits_to_string(bits: str) -> str:
    """Converts sequence of ascii bits back to the string"""
    # Fix missing leading zeros
    missing_zeros = (_char_length - len(bits) % _char_length) % _char_length
    bits = '0' * missing_zeros + bits
    return "".join([chr(int(bits[i: i+_char_length], 2)) for i in range(0, len(bits), _char_length)])


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