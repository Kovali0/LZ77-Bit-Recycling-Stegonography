import random


def random_msg(alphabet, length):
    """Generates random message an alphabet"""
    return "".join([random.choice(alphabet) for i in range(length)])


def prob_word_in_msg(word_length, msg_length, alphabet_size):
    """Calculates probability that a word will appear in a message, given their
    lengths and the size of the alphabet"""
    return 1 - (1 - 1/alphabet_size ** word_length) ** (max(msg_length - word_length, 0))


def approx_cnt_word_in_msg(word_length, msg_length, alphabet_size):
    """Calculates approximate number of times a word will appear in random message,
    given their lengths and the size of the alphabet"""
    return (msg_length - word_length) / alphabet_size ** word_length


class LZCoder:
    """Performs the very basic LZ77 encoding & decoding"""
    sep1 = chr(31)
    sep2 = chr(30)
    max_offset = 100
    max_lookahead = 100

    @staticmethod
    def encode(msg):
        msg_enc = ""
        cursor = 0
        # advance the cursor through the whole message
        while cursor < len(msg):
            lookahead = 1
            offset = 0
            # find the longest buffer that appeared before in the message
            # previous part to look for the repeated string
            msg_offset = msg[max(cursor - LZCoder.max_offset, 0): cursor]
            while lookahead <= LZCoder.max_lookahead:
                buffer_end = cursor + lookahead
                if buffer_end > len(msg):
                    break
                # next buffer to be copied from a previous subsequence
                buffer = msg[cursor: buffer_end]
                copy_pos = msg_offset.rfind(buffer)
                if copy_pos == -1:
                    break
                else:
                    offset = len(msg_offset) - copy_pos
                lookahead += 1
            # Decrement lookahead to the largest acceptable value
            lookahead -= 1
            # olc - offset+length+character triple
            olc = LZCoder.sep2 + str(offset) + LZCoder.sep1 + str(lookahead) \
                        + LZCoder.sep1
            cursor += lookahead
            if cursor < len(msg):
                olc += msg[cursor]
            msg_enc += olc
            cursor += 1
        # first character is a separator, ignore it
        return msg_enc[1:]

    @staticmethod
    def decode(msg_enc):
        if msg_enc == "":
            return ""
        msg_dec = ""
        # offset+length+character triples
        olc_s = msg_enc.split(LZCoder.sep2)
        for olc in olc_s:
            offset, length, character = olc.split(LZCoder.sep1)
            offset, length = int(offset), int(length)
            msg_dec += msg_dec[len(msg_dec)-offset: len(msg_dec)-offset+length] + character
        return msg_dec


if __name__ == '__main__':

    # str1 = "AABABAABBABABBBBBABBABABBBB"
    # str1_enc = LZCoder.encode(str1)
    # print(str1_enc)
    # str1_dec = LZCoder.decode(str1_enc)
    # print(str1_dec)

    alphabet1 = ['A', 'AAB', 'ACBC', 'CAB', 'BC']
    # alphabet1 = ['ABBA', 'AAB']
    msg1 = random_msg(alphabet1, 10)
    # msg1 = "AABACBCAABAACBCACBCAAABAABBC"
    print(msg1)
    msg1_enc = LZCoder.encode(msg1)
    print(msg1_enc)
    print("original length:", len(msg1))
    print("encoded length:", len(msg1_enc))
    print("ratio:", len(msg1_enc) / len(msg1))
    print("encoded ~spaces:", len(msg1_enc.replace(' ', '')))
    msg1_dec = LZCoder.decode(msg1_enc)
    print(msg1_dec)
    print(msg1 == msg1_dec)
    print(msg1[:-1] == msg1_dec[:-1])
