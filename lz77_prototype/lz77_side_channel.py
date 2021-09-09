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
    # Minimum match length, dependent on the format of encoding of a match
    min_lookahead = 6
    limit_lookbehind = True

    def __init__(self):
        # Numeral system coder
        # self._ns_coder = NumeralSystemCoder(limits=[])
        # self._ns_coder = None
        # Limits of the numeral system coder
        self._ns_limits = []
        # Array of unencoded "raw" string blocks
        self._enc_raw_blocks = []
        # Array of (distances, length) doubles
        self._enc_dists_length = []
        # Capacity of the hidden channel in bits
        self._hidden_capacity = None

    def start_encoding_get_capacity(self, data) -> int:
        """:returns: side channel capacity in bits. If 0, no hidden message can be stored."""
        # data_enc = ""
        cursor = 0
        # Number of different messages that can be stored in the side channel
        hidden_capacity_sum = 0
        # unencoded block of characters
        raw_block = ""

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
                match_distances = [len(data_offset) - m.start() - lookahead
                                   for m in re.finditer(buffer, data_offset)]
                num_of_choices = len(match_distances)
                # If there are many choices
                if num_of_choices > 1:
                    # Count to the length of the side channel
                    hidden_capacity_sum += math.log2(num_of_choices)
                    self._ns_limits.append(num_of_choices)

                cursor += lookahead
                # Save the double
                self._enc_dists_length.append((match_distances, lookahead))

                # reset current raw block
                self._enc_raw_blocks.append(raw_block)
                raw_block = ""
            else:
                # Emit next character to the raw block
                raw_block += data[cursor]
                cursor += 1

        # save remaining raw block (might be empty)
        self._enc_raw_blocks.append(raw_block)
            # if cursor < len(data):
            #     character = data[cursor]
            # else:
            #     character = ''

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
            dist_length_str = LZ77MultiChoiceCoder._sep2 + str(chosen_distance) + LZ77MultiChoiceCoder._sep1 \
                        + str(dists_length[1]) + LZ77MultiChoiceCoder._sep2
            data_enc += dist_length_str
        # add remaining raw block
        data_enc += self._enc_raw_blocks[-1]
        return data_enc

    @staticmethod
    def decode(data_enc) -> (str, str):
        """Decodes both explicit compressed data and the hidden channel binary stream"""
        if data_enc == "":
            return ""
        data_dec = ""
        distance_numbers = []
        distance_choices = []

        while True:
            # break if sep2 is not found
            sep2_pos = data_enc.find(LZ77MultiChoiceCoder._sep2)
            if sep2_pos == -1:
                break
            # copy next raw block
            data_dec += data_enc[:sep2_pos]
            data_enc = data_enc[sep2_pos+1:]
            sep1_pos = data_enc.find(LZ77MultiChoiceCoder._sep1)
            sep2_pos = data_enc.find(LZ77MultiChoiceCoder._sep2)
            # decode next matched substring
            match_dist = int(data_enc[:sep1_pos])
            match_length = int(data_enc[sep1_pos+1: sep2_pos])
            match_start = len(data_dec) - match_dist
            matched_substring = data_dec[match_start-match_length: match_start]
            # define offset to look for matches
            if LZ77MultiChoiceCoder.limit_lookbehind:
                data_offset = data_dec[max(0, len(data_dec) - LZ77MultiChoiceCoder.max_lookbehind):]
            else:
                data_offset = data_dec
            data_dec += matched_substring
            data_enc = data_enc[sep2_pos+1:]
            # get distances of all possible matches
            match_distances = [len(data_offset) - m.start() - match_length for m in re.finditer(matched_substring, data_offset)]
            # if there were many choices
            if len(match_distances) > 1:
                # get index of the chosen match distance
                distance_idx = match_distances.index(match_dist)
                distance_numbers.append(len(match_distances))
                distance_choices.append(distance_idx)
        # copy remaining raw block
        data_dec += data_enc

        # DLCs = data_enc.split(LZ77MultiChoiceCoder._sep2)
        # for DLC in DLCs:
        #     distance, length, character = DLC.split(LZ77MultiChoiceCoder._sep1)
        #     distance, length = int(distance), int(length)
        #     # the repeated and copied part of data
        #     matched_substring = data_dec[len(data_dec) - distance: len(data_dec) - distance + length]
        #     if LZ77MultiChoiceCoder.limit_lookbehind:
        #         data_offset = data_dec[max(0, len(data_dec) - LZ77MultiChoiceCoder.max_lookbehind):]
        #     else:
        #         data_offset = data_dec
        #     data_dec += matched_substring + character
        #     # get distances of all possible matches
        #     match_distances = [len(data_offset) - m.start() for m in re.finditer(matched_substring, data_offset)]
        #     # get index of the chosen match distance
        #     distance_idx = match_distances.index(distance)
        #     if len(match_distances) > 1:
        #         distance_numbers.append(len(match_distances))
        #         distance_choices.append(distance_idx)
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
    hidden_msg1 = "Will u marry me?"
    hidden_msg1_len = string_binary.length_of_bits(hidden_msg1)
    print("hidden message length: {} characters".format(len(hidden_msg1)))
    if hidden_msg1_len > msg1_n_hidden_bits:
        print("Hidden message too long!!")
    print("hidden message:", hidden_msg1)
    msg1_enc = lz_coder.complete_encoding_hide_message(hidden_msg1)
    msg1_enc_len = len(msg1_enc)

    # final distances in encoded msg1
    msg1_enc_distances = [int(m.group(0)) for m in re.finditer('[0-9]+', msg1_enc)]
    msg1_enc_reduced_numbers = [len(str(d)) - math.ceil(math.log(d, 254)) for d in msg1_enc_distances]
    msg1_enc_extra_len = msg1_enc_len - sum(msg1_enc_reduced_numbers)
    print("Encoded message length:", msg1_enc_len)
    print("Encoded message, reduced:", msg1_enc_extra_len)
    print("Compression ratio:", msg1_enc_len / len(msg1))
    # print("encoded msg1:", msg1_enc)
    msg1_dec, hidden_msg1_dec = LZ77MultiChoiceCoder.decode(msg1_enc)
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
