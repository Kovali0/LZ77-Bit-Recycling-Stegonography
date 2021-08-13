import random
import re
import bisect
# from .lz77_one import random_msg

def random_msg(alphabet, length):
    """Generates random message from an alphabet"""
    return "".join([random.choice(alphabet) for i in range(length)])



class LZ77MultiChoiceCoder:

    _sep1 = '-'
    _sep2 = '_'
    max_lookbehind = 500
    max_lookahead = 20
    limit_lookbehind = True

    @staticmethod
    def encode(data):
        data_enc = ""
        cursor = 0
        # List of choices of distances to form a side channel (for testing)
        match_distance_choices = []
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
                    break
                lookahead += 1

            # Decrement lookahead to the largest acceptable value
            lookahead -= 1
            # Cut buffer by one (to the longest matched)
            buffer = buffer[:-1]
            # Distances from starting positions of matches to the cursor
            match_distances = [len(data_offset) - m.start() for m in re.finditer(buffer, data_offset)]
            # Choice of one distance - random
            dist_choice_no = random.randint(0, len(match_distances)-1)
            match_distance_choices.append((dist_choice_no, len(match_distances)))
            # DLC - distance, length, character triple
            DLC = LZ77MultiChoiceCoder._sep2 + str(match_distances[dist_choice_no]) \
                  + LZ77MultiChoiceCoder._sep1 + str(lookahead) + LZ77MultiChoiceCoder._sep1
            cursor += lookahead
            if cursor < len(data):
                DLC += data[cursor]
            data_enc += DLC
            cursor += 1
        print("side channel:", match_distance_choices)
        # first character is a separator, ignore it
        return data_enc[1:]

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
                data_offset = data_dec[max(0, len(data_enc) - LZ77MultiChoiceCoder.max_lookbehind):]
            else:
                data_offset = data_dec
            data_dec += matched_substring + character
            # get distances of all possible matches
            match_distances = [len(data_offset) - m.start() for m in re.finditer(matched_substring, data_offset)]
            # get index of the chosen match distance
            # distance_idx = bisect.bisect_left(match_distances, distance)
            distance_idx = match_distances.index(distance)
            distance_choices.append((distance_idx, len(match_distances)))
        return data_dec, distance_choices




if __name__ == '__main__':
    alphabet = ['A', 'B']
    msg1 = random_msg(alphabet, 40)
    # msg1 = 'BBBBAABBBBBBABBABABABBBBBBAABBBAAAABABBA'
    print(msg1)
    msg1_enc = LZ77MultiChoiceCoder.encode(msg1)
    print(msg1_enc)
    msg1_dec, dist_choices = LZ77MultiChoiceCoder.decode(msg1_enc)
    print(msg1_dec)
    print(dist_choices)
    print(msg1 == msg1_dec)
