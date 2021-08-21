import random
import re
import math
import numpy as np
# from .lz77_one import random_msg
from numeral_system_coder import NumeralSystemCoder
import string_binary

def random_msg(alphabet, length):
    """Generates random message from an alphabet"""
    return "".join([random.choice(alphabet) for i in range(length)])


class LZ77MultiChoiceCoder:

    _sep1 = '-'
    _sep2 = '_'
    max_lookbehind = 25000
    max_lookahead = 50
    limit_lookbehind = True

    def __init__(self):
        # Numeral system coder
        # self._ns_coder = NumeralSystemCoder(limits=[])
        # self._ns_coder = None
        # Limits of the numeral system coder
        self._ns_limits = []
        # Array of (distances, length, character) triples
        self._DLC = []
        # Capacity of the hidden channel in bits
        self._hidden_capacity = None

    def start_encoding_get_capacity(self, data) -> int:
        """:returns: side channel capacity in bits"""
        data_enc = ""
        cursor = 0
        # Number of different messages that can be stored in the side channel
        hidden_capacity_sum = 0
        # advance the cursor through the whole message
        while cursor < len(data):
            if LZ77MultiChoiceCoder.limit_lookbehind:
                # data segment to look for matches
                data_offset = data[max(cursor - LZ77MultiChoiceCoder.max_lookbehind, 0): cursor]
            else:
                data_offset = data[0: cursor]
            # number of bytes (starting from the cursor) to search for matches
            lookahead = 1
            # next segment of the data to be matched
            buffer = ""
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
            # All match distances to choose from
            match_distances = [len(data_offset) - m.start() for m in re.finditer(buffer, data_offset)]
            num_of_choices = len(match_distances)
            if num_of_choices > 1:
                # Count to the length of the side channel
                hidden_capacity_sum += math.log2(num_of_choices)
                self._ns_limits.append(num_of_choices)

            cursor += lookahead
            if cursor < len(data):
                character = data[cursor]
            else:
                character = ''
            # Save the triple
            self._DLC.append((match_distances, lookahead, character))
            cursor += 1

        # print("side channel:", match_distance_choices)
        # first character is a separator, ignore it
        # print("Different messages to send:", side_channel_total_msgs)
        # side_channel_bits2 = int(math.floor(math.log2(side_channel_total_msgs)))
        self._hidden_capacity = int(math.floor(hidden_capacity_sum))
        return self._hidden_capacity

    def complete_encoding_hide_message(self, hidden_data: str) -> str:
        """Completes the compression along with storing hidden data"""
        # Convert binary stream to a sequence of choices of distances
        # self._ns_coder = NumeralSystemCoder(limits=self._ns_limits)
        # hidden_data_seq = self._ns_coder.bits_to_sequence(hidden_data)
        # Convert characters to bit sequence
        hidden_data = string_binary.string_to_bits(hidden_data)
        hidden_data_seq = NumeralSystemCoder.number_to_sequence(hidden_data, self._ns_limits)
        data_enc = ""
        h_i = 0
        for DLC in self._DLC:
            distances = DLC[0]
            # If there were many choices
            if len(distances) > 1:
                # Choose according to the sequence
                chosen_distance = distances[hidden_data_seq[h_i]]
                h_i += 1
            else:
                # otherwise, choose the only one
                chosen_distance = distances[0]
            # make the triple string
            DLC_str = str(chosen_distance) + LZ77MultiChoiceCoder._sep1 \
                        + str(DLC[1]) + LZ77MultiChoiceCoder._sep1 + DLC[2]
            data_enc += LZ77MultiChoiceCoder._sep2 + DLC_str
        return data_enc[1:]

    @staticmethod
    def decode(data_enc) -> (str, str):
        """Decodes both explicit compressed data and the hidden channel binary stream"""
        if data_enc == "":
            return ""
        data_dec = ""
        distance_numbers = []
        distance_choices = []
        DLCs = data_enc.split(LZ77MultiChoiceCoder._sep2)
        for DLC in DLCs:
            distance, length, character = DLC.split(LZ77MultiChoiceCoder._sep1)
            distance, length = int(distance), int(length)
            # the repeated and copied part of data
            matched_substring = data_dec[len(data_dec) - distance: len(data_dec) - distance + length]
            if LZ77MultiChoiceCoder.limit_lookbehind:
                data_offset = data_dec[max(0, len(data_dec) - LZ77MultiChoiceCoder.max_lookbehind):]
            else:
                data_offset = data_dec
            data_dec += matched_substring + character
            # get distances of all possible matches
            match_distances = [len(data_offset) - m.start() for m in re.finditer(matched_substring, data_offset)]
            # get index of the chosen match distance
            distance_idx = match_distances.index(distance)
            if len(match_distances) > 1:
                distance_numbers.append(len(match_distances))
                distance_choices.append(distance_idx)
        # ns_decoder = NumeralSystemCoder(limits=np.array(distance_numbers))
        # hidden_data = ns_decoder.sequence_to_bits(np.array(distance_choices))
        hidden_data = NumeralSystemCoder.sequence_to_number(distance_choices, distance_numbers)
        # Convert to characters
        hidden_data = string_binary.bits_to_string(hidden_data)
        return data_dec, hidden_data

    def hidden_capacity_bits(self) -> int:
        return self._hidden_capacity

    def hidden_capacity_characters(self) -> int:
        return self._hidden_capacity // string_binary._char_length

import os
if __name__ == '__main__':
    print(os.listdir('..\\sample_data'))
    fname = '..\\sample_data\\sampleFICT2.txt'
    with open(fname, 'r') as f:
        msg1 = f.read(10000)
    # alphabet = ['A', 'B', 'C']
    # msg1 = random_msg(alphabet, 30000)


    lz_coder = LZ77MultiChoiceCoder()
    msg1_n_hidden_bits = lz_coder.start_encoding_get_capacity(msg1)
    print("Hidden channel capacity: {} ({} characters)".format(msg1_n_hidden_bits,
                                                              lz_coder.hidden_capacity_characters()))
    # hidden_msg1 = "101101000100001001110000"
    # Sequence generated by a Numeral System Coder
    # hidden_msg1 = "101100101101111110101110001001010001101011110011001110011100111011111111101001101111010100111111"
    hidden_msg1 = "Will you marry me???"
    hidden_msg1_len = string_binary.length_of_bits(hidden_msg1)
    print("hidden message length: {} characters".format(len(hidden_msg1)))
    if hidden_msg1_len > msg1_n_hidden_bits:
        print("Hidden message too long!!")
    print("hidden message:", hidden_msg1)
    msg1_enc = lz_coder.complete_encoding_hide_message(hidden_msg1)
    msg1_enc_len = len(msg1_enc)
    print("Encoded message length:", msg1_enc_len)
    print("Compression ratio:", msg1_enc_len / len(msg1))
    # print("encoded msg1:", msg1_enc)
    msg1_dec, hidden_msg1_dec = LZ77MultiChoiceCoder.decode(msg1_enc)
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
