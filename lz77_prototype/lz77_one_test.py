import unittest
from .lz77_one import LZ77Coder


class LZCoderTest(unittest.TestCase):

    def test_encode_decode_1(self):
        msg = "AABABBBABBABBABBABABBBABABABABBAAABAAABABBAABBBABAABAABBBABB"
        msg_dec = LZ77Coder.decode(LZ77Coder.encode(msg))
        self.assertEqual(msg, msg_dec)

    def test_encode_decode_2(self):
        msg = "BAAEABAAEEDDAACADEDABDCBBCBCBDCBBCBEAABEABDEDAECDD"
        msg_dec = LZ77Coder.decode(LZ77Coder.encode(msg))
        self.assertEqual(msg, msg_dec)

    def test_encode_decode_3(self):
        msg = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        msg_dec = LZ77Coder.decode(LZ77Coder.encode(msg))
        self.assertEqual(msg, msg_dec)

    def test_encode_decode_4(self):
        msg = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et " \
              "dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut " \
              "aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum " \
              "dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui " \
              "officia deserunt mollit anim id est laborum."
        self.assertEqual(msg, LZ77Coder.decode(LZ77Coder.encode(msg)))

    def test_encode_decode_5(self):
        msg = "A" * 200
        self.assertEqual(msg, LZ77Coder.decode(LZ77Coder.encode(msg)))

    def test_encode_decode_single_char(self):
        self.assertEqual("A", LZ77Coder.decode(LZ77Coder.encode("A")))

    def test_encode_decode_empty(self):
        self.assertEqual("", LZ77Coder.decode(LZ77Coder.encode("")))

