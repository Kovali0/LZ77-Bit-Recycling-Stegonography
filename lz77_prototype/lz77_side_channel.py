import random
import math
import abc
# from .lz77_one import random_msg
import lz77_prototype.numeral_system_coder as nsc
import lz77_prototype.string_binary as string_binary
from lz77_prototype.search import find_last, find_all
import cProfile


def random_msg(alphabet, length):
    """Generates random message from an alphabet"""
    return "".join([random.choice(alphabet) for i in range(length)])


# TODO: make an abstract class LZ77MultiChoiceCoder, make two
# inherents that implement both encoding algorithms ("choose
# from all distances", "choose from last 2 distances")

class LZ77MultiChoiceCoder(abc.ABC):
    """Class responsible for encoding explicit & hidden message, calculating and returning information
    about hidden capacity, decoding explicit & hidden message"""

    # _sep1 = '-'
    # _sep2 = '_'
    _sep1 = chr(31)
    _sep2 = chr(30)
    max_lookbehind = 25000
    max_lookahead = 50
    # Minimum match length, dependent on the format of encoding of a match
    min_lookahead = 6
    limit_lookbehind = True

    def __init__(self):
        # Numeral system coder
        # self._ns_coder = NumeralSystemCoder(limits=[])
        # self._ns_coder = None
        # Array of unencoded "raw" string blocks
        self._enc_raw_blocks = []
        # Array of (distances, length) doubles
        self._enc_dists_length = []
        # Capacity of the hidden channel in bits
        self._hidden_capacity = None

    def start_encoding_get_capacity(self, data) -> int:
        """Starts encoding of a piece of data, calculates side channel capacity
        :returns: side channel capacity in bits. If 0, no hidden message can be stored."""
        # data_enc = ""
        cursor = 0
        # Number of different messages that can be stored in the side channel
        hidden_capacity_sum = 0
        # current unencoded block of characters
        cur_raw_block = ""

        # advance the cursor through the whole message
        while cursor < len(data):
            if LZ77MultiChoiceCoder.limit_lookbehind:
                # data segment to look for matches
                data_offset = data[max(cursor - LZ77MultiChoiceCoder.max_lookbehind, 0): cursor]
            else:
                data_offset = data[0: cursor]
            # number of bytes to search for matches
            lookahead = LZ77MultiChoiceCoder.min_lookahead
            # next segment of the data to be matched
            buffer = ""

            # Get the longest buffer that is matched in current offset
            while lookahead <= LZ77MultiChoiceCoder.max_lookahead:
                buffer_end = cursor + lookahead
                # If the buffer exceeds data sequence, stop
                if buffer_end > len(data):
                    break
                buffer = data[cursor: buffer_end]
                # check if the buffer is matched at least once
                if data_offset.find(buffer) == -1:
                    # Cut buffer by one (to the longest matched)
                    buffer = buffer[:-1]
                    break
                lookahead += 1

            # Decrement lookahead to the largest acceptable value
            lookahead -= 1

            # Is the match length at least minimal?
            if lookahead >= LZ77MultiChoiceCoder.min_lookahead:
                # All match distances to choose from
                # DIFFERENCE

                match_distances, extra_capacity = self._find_extra_block_matches(data_offset, buffer)

                hidden_capacity_sum += extra_capacity
                # match_distances = [len(data_offset) - m.start() - lookahead
                #                    for m in re.finditer(buffer, data_offset)]
                # num_of_choices = len(match_distances)
                # If there are many choices
                # if num_of_choices > 1:
                # Count to the length of the side channel
                # hidden_capacity_sum += math.log2(num_of_choices)
                # DIFFERENCE
                # self._ns_limits.append(num_of_choices)

                cursor += lookahead
                # Save the double
                self._enc_dists_length.append((match_distances, lookahead))

                # reset current raw block
                self._enc_raw_blocks.append(cur_raw_block)
                cur_raw_block = ""
            else:
                # Emit next character to the raw block
                cur_raw_block += data[cursor]
                cursor += 1

        # save remaining raw block (might be empty)
        self._enc_raw_blocks.append(cur_raw_block)

        # print("side channel:", match_distance_choices)
        # first character is a separator, ignore it
        # print("Different messages to send:", side_channel_total_msgs)
        # side_channel_bits2 = int(math.floor(math.log2(side_channel_total_msgs)))

        self._hidden_capacity = int(math.floor(hidden_capacity_sum))
        return self._hidden_capacity

    @abc.abstractmethod
    def _find_extra_block_matches(self, data_offset, buffer) -> tuple:
        """Finds extra matches of a buffer in the offset for the use of
        side channel.
        :returns: tuple (<list of distances of extra matches>,
        <extra capacity for the side channel>)"""
        pass

    def complete_encoding_hide_message(self, hidden_data: str) -> str:
        """Completes encoding and stores hidden message in the side channel
        :returns: compressed data with hidden message.
        If hidden_data size exceeds side channel capacity, explicit compression will
        succeed, but the hidden message will be damaged."""
        # Convert characters to sequence of numbers
        hidden_data_seq = self._convert_to_int_sequence(hidden_data)
        # print("Hidden data as sequence:", hidden_data_seq)
        data_enc = ""
        h_i = 0
        for raw_block, dists_length in zip(self._enc_raw_blocks, self._enc_dists_length):
            data_enc += raw_block
            distances = dists_length[0]
            # If there were many choices
            if len(distances) > 1:
                # Choose according to the sequence
                chosen_distance = distances[hidden_data_seq[h_i]]
                h_i += 1
            else:
                # otherwise, choose the only one
                chosen_distance = distances[0]
            # distance-length pair message
            dist_length_str = LZ77MultiChoiceCoder._sep2 + nsc.number_to_system(
                chosen_distance) + LZ77MultiChoiceCoder._sep1 \
                + nsc.number_to_system(dists_length[1]) + LZ77MultiChoiceCoder._sep2
            data_enc += dist_length_str
        # add remaining raw block
        data_enc += self._enc_raw_blocks[-1]
        return data_enc

    @abc.abstractmethod
    def _convert_to_int_sequence(self, data: str) -> list:
        """Converts data string to appropriate sequence of integers
        (will be mapped to choices of distances in the encoded message)"""
        pass

    @abc.abstractmethod
    def _convert_to_string(self, sequence: list) -> str:
        """Converts sequence of numbers to corresponding string message"""
        pass

    def decode(self, data_enc) -> (str, str):
        """Decodes both explicit compressed data and the hidden message.
        :returns: (<decoded data>, <decoded hidden message>)"""
        if data_enc == "":
            return "", ""
        data_dec = ""
        # --DIFFERENCE--
        self._decoding_init()
        distance_choices = []

        while True:
            # break if sep2 is not found
            sep2_pos = data_enc.find(LZ77MultiChoiceCoder._sep2)
            if sep2_pos == -1:
                break
            # copy next raw block
            data_dec += data_enc[:sep2_pos]
            data_enc = data_enc[sep2_pos + 1:]
            sep1_pos = data_enc.find(LZ77MultiChoiceCoder._sep1)
            sep2_pos = data_enc.find(LZ77MultiChoiceCoder._sep2)
            # decode next matched substring
            match_dist = nsc.system_to_number(data_enc[:sep1_pos])
            match_length = nsc.system_to_number(data_enc[sep1_pos + 1: sep2_pos])
            match_start = len(data_dec) - match_dist
            matched_substring = data_dec[match_start - match_length: match_start]
            # define offset to look for matches
            if LZ77MultiChoiceCoder.limit_lookbehind:
                data_offset = data_dec[max(0, len(data_dec) - LZ77MultiChoiceCoder.max_lookbehind):]
            else:
                data_offset = data_dec
            data_dec += matched_substring
            data_enc = data_enc[sep2_pos + 1:]
            # get distances of all possible matches
            # --DIFFERENCE--
            match_distances, _ = self._find_extra_block_matches(data_offset, matched_substring)

            # match_distances = [len(data_offset) - m.start() - match_length for m in
            #                    re.finditer(matched_substring, data_offset)]
            # if there were many choices
            if len(match_distances) > 1:
                # get index of the chosen match distance
                # --DIFFERENCE--
                distance_idx = match_distances.index(match_dist)
                distance_choices.append(distance_idx)
                # self._decoding_update_ns_limits(len(match_distances))

        # copy remaining raw block
        data_dec += data_enc

        # --DIFFERENCE--
        # print("Decoded hidden data as sequence:", distance_choices)
        hidden_data = self._convert_to_string(distance_choices)
        # hidden_data = nsc.NumeralSystemCoder.sequence_to_number(distance_choices, distance_numbers)
        # Convert to characters
        # hidden_data = string_binary.bits_to_string(hidden_data)
        return data_dec, hidden_data

    @abc.abstractmethod
    def _decoding_init(self):
        """Initializes process of decoding"""
        pass

    # @abc.abstractmethod
    def _decoding_update_ns_limits(self, n_match_distances: int):
        """Updates properly list of distance choices while decoding"""
        pass

    def hidden_capacity_bits(self) -> int:
        return self._hidden_capacity

    def hidden_capacity_characters(self) -> int:
        return self._hidden_capacity // string_binary._char_length


class LZ77AllChoicesCoder(LZ77MultiChoiceCoder):

    def _decoding_init(self):
        self._ns_limits = []

    def _decoding_update_ns_limits(self, n_match_distances: int):
        self._ns_limits.append(n_match_distances)

    def __init__(self):
        super().__init__()
        # Limits of the numeral system coder
        self._ns_limits = []

    def _find_extra_block_matches(self, data_offset, buffer) -> tuple:
        """Implements finding extra matches of a block (buffer).
        Searches for all matches in the offset"""
        match_distances = [len(data_offset) - pos - len(buffer)
                           for pos in find_all(buffer, data_offset)]
        num_of_choices = len(match_distances)
        if num_of_choices > 1:
            self._ns_limits.append(num_of_choices)
        return match_distances, math.log2(num_of_choices)

    def _convert_to_int_sequence(self, data: str) -> list:
        return nsc.NumeralSystemCoder.number_to_sequence(
            string_binary.string_to_bits(data), self._ns_limits
        )

    def _convert_to_string(self, sequence: list) -> str:
        return string_binary.bits_to_string(
            nsc.NumeralSystemCoder.sequence_to_number(sequence, self._ns_limits)
        )


class LZ77LastTwoChoicesCoder(LZ77MultiChoiceCoder):

    def _decoding_init(self):
        pass

    # def _decoding_update_ns_limits(self, n_match_distances: int):
    #     pass

    def __init__(self):
        super().__init__()

    def _find_extra_block_matches(self, data_offset, buffer) -> tuple:
        """Implements finding extra matches of a block (buffer).
        Searches for last two matches in the offset"""
        match_distances = [len(data_offset) - pos - len(buffer)
                           for pos in find_last(buffer, data_offset, 2)]
        # Equivalent to: math.log2(len(match_distances))
        extra_capacity = 1 if len(match_distances) == 2 else 0
        return match_distances, extra_capacity

    def _convert_to_int_sequence(self, data: str) -> list:
        # Convert to binary sequence, fill with zeros up to the number of distance-length doubles
        return string_binary.string_to_bit_arr(data) + [0] * (len(self._enc_dists_length) - len(data))

    def _convert_to_string(self, sequence: list) -> str:
        # Convert bits to string, ignore trailing zeros
        k = 0
        while sequence[k: k + string_binary._char_length] != [0] * string_binary._char_length:
            k += string_binary._char_length
        return string_binary.bit_arr_to_string(sequence[:k])


import os


def test_capacity():
    # msg2 = random_msg(['A', 'B'], 20000)
    print(os.listdir('..\\sample_data'))
    fname = '..\\sample_data\\dickens.txt'
    with open(fname) as f:
        msg2 = f.read(25000)
    # print(f"Message: {msg2}")
    coder = LZ77LastTwoChoicesCoder()
    coder.start_encoding_get_capacity(msg2)
    print(f"Side channel capacity: {coder.hidden_capacity_bits()} bits"
          f" ({coder.hidden_capacity_characters()} characters)")


def test_all():
    print(os.listdir('..\\sample_data'))
    fname = '..\\sample_data\\dickens.txt'
    with open(fname, 'r') as f:
        msg1 = f.read(40000)
    # alphabet = ['A', 'B']
    # msg1 = random_msg(alphabet, 10000)

    lz_coder = LZ77LastTwoChoicesCoder()
    msg1_n_hidden_bits = lz_coder.start_encoding_get_capacity(msg1)
    print("Hidden channel capacity: {} ({} characters)".format(msg1_n_hidden_bits,
                                                               lz_coder.hidden_capacity_characters()))
    # hidden_msg1 = "101101000100001001110000"
    # Sequence generated by a Numeral System Coder
    # hidden_msg1 = "101100101101111110101110001001010001101011110011001110011100111011111111101001101111010100111111"
    hidden_msg1 = "     Will u marry me?   "
    # hidden_msg1 = ""
    hidden_msg1_len = string_binary.length_of_bits(hidden_msg1)
    print("hidden message length: {} characters".format(len(hidden_msg1)))
    if hidden_msg1_len > msg1_n_hidden_bits:
        print("Hidden message too long!!")
    print("hidden message:", hidden_msg1)
    msg1_enc = lz_coder.complete_encoding_hide_message(hidden_msg1)
    msg1_enc_len = len(msg1_enc)

    # final distances in encoded msg1
    # msg1_enc_distances = [int(m.group(0)) for m in re.finditer('[0-9]+', msg1_enc)]
    # msg1_enc_reduced_numbers = [len(str(d)) - math.ceil(math.log(d, 254)) for d in msg1_enc_distances]
    # msg1_enc_extra_len = msg1_enc_len - sum(msg1_enc_reduced_numbers)
    print("Encoded message length:", msg1_enc_len)
    # print("Encoded message, reduced:", msg1_enc_extra_len)
    print("Compression ratio:", msg1_enc_len / len(msg1))
    # print("encoded msg1:", msg1_enc)
    msg1_dec, hidden_msg1_dec = lz_coder.decode(msg1_enc)
    # print("decoded msg1:", msg1_dec)
    print("hidden msg decoded:", hidden_msg1_dec)
    print("messages equal:", msg1 == msg1_dec)
    print("hidden msgs equal:", hidden_msg1 == hidden_msg1_dec)

    # # msg1 = 'BBABBBABBAABBAABBABBABBABBABABBBBAAABBAB'
    # # print(msg1)
    # msg1_enc, dist_choices_enc = LZ77MultiChoiceCoder.encode_random_choices(msg1)
    # # print(msg1_enc)
    # msg1_dec, dist_choices_dec = LZ77MultiChoiceCoder.decode_with_distances(msg1_enc)
    # # print(msg1_dec)
    # print("msg1 == msg1_dec:", msg1 == msg1_dec)
    # # print("dist_choices_enc:", dist_choices_enc)
    # # print("dist_choices_dec:", dist_choices_dec)
    # print("dist choices equal:", dist_choices_dec == dist_choices_enc)


if __name__ == '__main__':
    cProfile.run("test_all()", sort="cumtime")
