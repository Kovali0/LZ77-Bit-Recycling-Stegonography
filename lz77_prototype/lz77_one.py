import random


def random_msg(alphabet, length):
    """Generates random message from an alphabet"""
    return "".join([random.choice(alphabet) for i in range(length)])


def prob_word_in_msg(word_length, msg_length, alphabet_size):
    """Calculates probability that a word will appear in a message, given their
    lengths and the size of the alphabet"""
    return 1 - (1 - 1/alphabet_size ** word_length) ** (max(msg_length - word_length, 0))


def approx_cnt_word_in_msg(word_length, msg_length, alphabet_size):
    """Calculates approximate number of times a word will appear in random message,
    given their lengths and the size of the alphabet"""
    return (msg_length - word_length) / alphabet_size ** word_length


class LZ77Coder:
    """Performs the very basic LZ77 encoding & decoding"""
    # sep1 = chr(31)
    # sep2 = chr(30)
    _sep1 = '-'
    _sep2 = '_'
    max_offset = 100
    max_lookahead = 100

    @staticmethod
    def encode(msg):
        msg_enc = ""
        cursor = 0
        # advance the cursor through the whole message
        while cursor < len(msg):
            # number of bytes from cursor to be searched
            lookahead = 1
            # distance of the match from the cursor
            match_distance = 0
            # find the longest buffer that appeared before in the message
            # previous part to look for the repeated string
            msg_offset = msg[max(cursor - LZ77Coder.max_offset, 0): cursor]
            while lookahead <= LZ77Coder.max_lookahead:
                buffer_end = cursor + lookahead
                if buffer_end > len(msg):
                    break
                # next buffer to be copied from a previous subsequence
                buffer = msg[cursor: buffer_end]
                copy_pos = msg_offset.rfind(buffer)
                if copy_pos == -1:
                    break
                else:
                    match_distance = len(msg_offset) - copy_pos
                lookahead += 1
            # Decrement lookahead to the largest acceptable value
            lookahead -= 1
            # dlc - distance+length+character triple
            dlc = LZ77Coder._sep2 + str(match_distance) + LZ77Coder._sep1 + str(lookahead) \
                  + LZ77Coder._sep1
            cursor += lookahead
            if cursor < len(msg):
                dlc += msg[cursor]
            msg_enc += dlc
            cursor += 1
        # first character is a separator, ignore it
        return msg_enc[1:]

    @staticmethod
    def decode(msg_enc):
        if msg_enc == "":
            return ""
        msg_dec = ""
        # offset+length+character triples
        olc_s = msg_enc.split(LZ77Coder._sep2)
        for olc in olc_s:
            offset, length, character = olc.split(LZ77Coder._sep1)
            offset, length = int(offset), int(length)
            msg_dec += msg_dec[len(msg_dec)-offset: len(msg_dec)-offset+length] + character
        return msg_dec





if __name__ == '__main__':

    # str1 = "AABABAABBABABBBBBABBABABBBB"
    # str1_enc = LZ77Coder.encode(str1)
    # print(str1_enc)
    # str1_dec = LZ77Coder.decode(str1_enc)
    # print(str1_dec)

    # alphabet1 = ['AAB', 'ACBC', 'CAB', 'BC']
    # alphabet1 = ['ABBA', 'AAB']
    alphabet1 = ['A', 'B']
    msg1 = random_msg(alphabet1, 500)
    # msg1 = "AABACBCAABAACBCACBCAAABAABBC"
    print(msg1)
    msg1_enc = LZ77Coder.encode(msg1)
    print(msg1_enc)
    print("original length:", len(msg1))
    print("encoded length:", len(msg1_enc))
    print("ratio:", len(msg1_enc) / len(msg1))
    print("encoded ~separator 1:", len(msg1_enc.replace(LZ77Coder._sep1, '')))
    msg1_dec = LZ77Coder.decode(msg1_enc)
    print(msg1_dec)
    print(msg1 == msg1_dec)
    print(msg1[:-1] == msg1_dec[:-1])
