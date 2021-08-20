import numpy as np


class NumeralSystemCoder:
    """Codes a sequence (s1,s2,...,s_m) in a numeral system (n1,n2,...n_m),
     where 0 <= s_i < n_i for i=1,2,...,m. The sequence is coded into a bit stream
     and vice versa."""

    def __init__(self, limits, norm_shift=16, norm_limit=(1 << 32)):
        """:param limits: limits in the numeral system"""
        self.limits = np.array(limits).astype(np.int64)
        self.__norm_shift = norm_shift
        self.__norm_limit_up = norm_limit
        self.__norm_limit_low = 1 << norm_shift

    def get_capacity(self):
        """Calculates the capacity of the numeral system - maximum length of a
        binary stream that can be coded within this system
        E.g. numeral system with limits = [5, 8, 14, 11, 7, 6] can encode
        5*8*14*11*7*6=258720 different messages, so it can use
        floor(log2(258720)) = floor(17.98) = 17 bits"""
        return int(np.floor(sum(np.log2(i) for i in self.limits)))

    @staticmethod
    def sequence_to_number(seq, n_lims) -> str:
        """Codes a sequence in given numeral system into a number"""
        res = 0
        for i in range(len(n_lims)):
            res = int(seq[i]) + int(n_lims[i]) * res
        return bin(res).replace('0b', '')

    @staticmethod
    def number_to_sequence(code, n_lims) -> list:
        code = int(code, 2)
        seq = []
        for n_i in n_lims[::-1]:
            seq.append(code % n_i)
            code = code // n_i
        return seq[::-1]

    def sequence_to_bits(self, seq: np.ndarray) -> str:
        """Codes a sequence of integer numbers in the numeral system to the binary stream"""
        seq, limits = seq.astype(np.int64), self.limits.astype(np.int64)
        res = ""
        # Temporary code value
        code_tmp = 0
        for i in range(len(limits)):
            # print(f"{i}: {code_tmp}")
            code_new = seq[i] + limits[i] * code_tmp
            # Value above the limit - renormalization
            if code_new >= self.__norm_limit_up:
                # Append last 16 digits from current code
                res += bin(code_tmp)[-self.__norm_shift:]
                code_tmp >>= self.__norm_shift
            code_tmp = seq[i] + limits[i] * code_tmp
        res += bin(code_tmp).replace("0b", "")
        return res

    def bits_to_sequence(self, code_bin: str) -> np.ndarray:
        """Codes a binary stream into the sequence of integers in the numeral system"""
        # Decoded sequence
        res = []
        rem_bits = len(code_bin) % self.__norm_shift + self.__norm_shift
        code_tmp = int(code_bin[-rem_bits:], 2)
        code_bin = code_bin[:-rem_bits]
        for i in range(len(self.limits)-1, -1, -1):
            res.append(code_tmp % self.limits[i])
            code_tmp //= self.limits[i]
            # Renormalization
            if code_tmp < self.__norm_limit_low:
                if len(code_bin) > 0:
                    code_tmp <<= self.__norm_shift
                    code_tmp += int(code_bin[-self.__norm_shift:], 2)
                    code_bin = code_bin[:-self.__norm_shift]
        return np.array(res[::-1])


if __name__ == '__main__':
    # pass
    # Example numeral system
    n2_lims = np.array([811, 110, 121, 225, 219, 27, 23, 22, 110, 127, 240, 240, 340, 350, 23, 24, 99, 199, 300])
    # number of bits that can be stored in it
    n2_capacity = int(np.floor(sum(np.log2(i) for i in n2_lims)))
    print("n2 capacity:", n2_capacity, "bits")
    # sample bit message to encode in the n2 system
    msg2 = "1010111010101010101011010010101010101010101011111111111100000000"
    # msg2 = 53 * "0"
    print("bin message:", msg2)
    n2_coder = NumeralSystemCoder(n2_lims)
    msg2_enc = n2_coder.bits_to_sequence(msg2)
    print("n2 encoded:", msg2_enc)
    msg2_dec = n2_coder.sequence_to_bits(msg2_enc)
    print("decoded bin message:", msg2_dec)
    print("msg2 == msg2_dec:", msg2 == msg2_dec)
