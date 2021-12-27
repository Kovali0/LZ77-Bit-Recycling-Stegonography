import random
import lz77_prototype.numeral_system_coder as nsc


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
    _sep1 = chr(31)
    _sep2 = chr(30)
    # _sep1 = '-'
    # _sep2 = '_'
    max_offset = 50000
    max_lookahead = 50
    # minimum length of a match, based on format of encoding of the match
    min_lookahead = 5

    @staticmethod
    def encode(msg):
        msg_enc = ""
        cursor = 0
        # advance the cursor through the whole message
        while cursor < len(msg):
            # number of bytes from cursor to be searched
            lookahead = LZ77Coder.min_lookahead
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
                    match_distance = len(msg_offset) - copy_pos - lookahead
                lookahead += 1
            # Decrement lookahead to the largest acceptable value
            lookahead -= 1
            # distance+length double
            dist_length = LZ77Coder._sep2 + str(match_distance) + LZ77Coder._sep1 \
                          + str(lookahead) + LZ77Coder._sep2
            # cursor += lookahead
            # if cursor < len(msg):
            #     dist_length += msg[cursor]

            # Is encoded message shorter than the match?
            if len(dist_length) <= lookahead:
                msg_enc += dist_length
                cursor += lookahead
            else:
                # Emit only next character
                msg_enc += msg[cursor]
                cursor += 1
        return msg_enc

    @staticmethod
    def decode(msg_enc):
        if msg_enc == "":
            return ""
        msg_dec = ""
        while True:
            # copy next unencoded substring
            # break if sep2 is not found
            sep2_pos = msg_enc.find(LZ77Coder._sep2)
            if sep2_pos == -1:
                break
            msg_dec += msg_enc[:sep2_pos]
            msg_enc = msg_enc[sep2_pos+1:]
            sep1_pos = msg_enc.find(LZ77Coder._sep1)
            sep2_pos = msg_enc.find(LZ77Coder._sep2)
            # decode and copy next matched substring
            match_dist = int(msg_enc[:sep1_pos])
            match_length = int(msg_enc[sep1_pos+1: sep2_pos])
            match_start = len(msg_dec) - match_dist
            msg_dec += msg_dec[match_start-match_length: match_start]
            msg_enc = msg_enc[sep2_pos+1:]
        # copy remaining substring
        msg_dec += msg_enc
        return msg_dec


if __name__ == '__main__':

    # str1 = "AABABAABBABABBBBBABBABABBBB"
    # str1_enc = LZ77Coder.encode(str1)
    # print(str1_enc)
    # str1_dec = LZ77Coder.decode(str1_enc)
    # print(str1_dec)

    # alphabet1 = ['AAB', 'ACBC', 'CAB', 'BC']
    # alphabet1 = ['ABBA', 'AAB']
    # with open('..\\sample_data\\sampleFICT2.txt') as f:
    #     msg1 = f.read(75000)
    alphabet1 = ['A', 'B']
    msg1 = random_msg(alphabet1, 200)
    # msg1 = "BABAABAAABAAABABABABBAAABABABBAABBBAABBBBABBABAABABBAAABAABAABAABBABAA"
    print(msg1)
    msg1_enc = LZ77Coder.encode(msg1)
    print(msg1_enc)
    msg1_dec = LZ77Coder.decode(msg1_enc)
    # print(msg1_dec)
    print("original length:", len(msg1))
    print("encoded length:", len(msg1_enc))
    print("ratio:", len(msg1_enc) / len(msg1))
    # remove consequently appearing separators
    msg1_enc_v2 = msg1_enc.replace(LZ77Coder._sep2 * 2, LZ77Coder._sep2)
    # print("encoded v2:", msg1_enc_v2)
    print("encoded v2 length:", len(msg1_enc_v2))
    print("encoded v2 ratio:", len(msg1_enc_v2) / len(msg1))
    print("msg1 == msg1_dec:", msg1 == msg1_dec)
    # print(msg1[:-1] == msg1_dec[:-1])
