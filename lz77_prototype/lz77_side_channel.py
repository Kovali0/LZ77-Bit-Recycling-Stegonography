import random
import re
import math
import bisect
# from .lz77_one import random_msg

def random_msg(alphabet, length):
    """Generates random message from an alphabet"""
    return "".join([random.choice(alphabet) for i in range(length)])



class LZ77MultiChoiceCoder:

    _sep1 = '-'
    _sep2 = '_'
    max_lookbehind = 5000
    max_lookahead = 30
    limit_lookbehind = True

    @staticmethod
    def encode(data):
        data_enc = ""
        cursor = 0
        # List of choices of distances to form a side channel (for testing)
        match_distance_choices = []
        # Number of different messages that can be stored in the side channel
        # side_channel_total_msgs = 1
        side_channel_capacity = 0
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
            # Distances from starting positions of matches to the cursor
            match_distances = [len(data_offset) - m.start() for m in re.finditer(buffer, data_offset)]
            num_of_choices = len(match_distances)
            # Choice of one distance - random
            dist_choice_no = random.randint(0, num_of_choices-1)
            if num_of_choices > 1:
                match_distance_choices.append((dist_choice_no, len(match_distances)))
                # side_channel_total_msgs *= num_of_choices
                side_channel_capacity += math.log2(num_of_choices)
            # DLC - distance, length, character triple
            DLC = LZ77MultiChoiceCoder._sep2 + str(match_distances[dist_choice_no]) \
                  + LZ77MultiChoiceCoder._sep1 + str(lookahead) + LZ77MultiChoiceCoder._sep1
            cursor += lookahead
            if cursor < len(data):
                DLC += data[cursor]
            data_enc += DLC
            cursor += 1
        # print("side channel:", match_distance_choices)
        # first character is a separator, ignore it
        print("Side channel:")
        # print("Different messages to send:", side_channel_total_msgs)
        # side_channel_bits2 = int(math.floor(math.log2(side_channel_total_msgs)))
        # print("side_channel_bits2:", side_channel_bits2)
        side_channel_bits = int(math.floor(side_channel_capacity))
        print("Channel capacity: {} bits ({} bytes)".format(side_channel_bits, side_channel_bits / 8))
        return data_enc[1:], match_distance_choices

    @staticmethod
    def decode(data_enc):
        """Decodes both explicit compressed data and message from the hidden channel"""
        if data_enc == "":
            return ""
        data_dec = ""
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
            # distance_idx = bisect.bisect_left(match_distances, distance)
            distance_idx = match_distances.index(distance)
            if len(match_distances) > 1:
                distance_choices.append((distance_idx, len(match_distances)))
        return data_dec, distance_choices




if __name__ == '__main__':
    alphabet = ['A', 'B']
    msg1 = random_msg(alphabet, 50000)
    # msg1 = 'BBABBBABBAABBAABBABBABBABBABABBBBAAABBAB'
    # print(msg1)
    msg1_enc, dist_choices_enc = LZ77MultiChoiceCoder.encode(msg1)
    # print(msg1_enc)
    msg1_dec, dist_choices_dec = LZ77MultiChoiceCoder.decode(msg1_enc)
    # print(msg1_dec)
    print("msg1 == msg1_dec:", msg1 == msg1_dec)
    # print("dist_choices_enc:", dist_choices_enc)
    # print("dist_choices_dec:", dist_choices_dec)
    print("dist choices equal:", dist_choices_dec == dist_choices_enc)
