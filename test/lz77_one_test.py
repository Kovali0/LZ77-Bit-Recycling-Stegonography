import unittest
import os
from lz77_prototype.lz77_one import LZ77Coder
from lz77_prototype.lz77_side_channel import LZ77MultiChoiceCoder, LZ77AllChoicesCoder, LZ77LastTwoChoicesCoder
from generate_test_data import DATA_PATH


class LZCoderTest(unittest.TestCase):

    def test_encode_decode(self, msg):
        msg_dec = LZ77Coder.decode(LZ77Coder.encode(msg))
        self.assertEqual(msg, msg_dec)

    def test_enc_dec_all(self):
        for tfname in ['t01', 't02', 't03', 't04', 't05', 't06', 't07']:
            with open(os.path.join(DATA_PATH, tfname), 'r') as tf:
                with self.subTest(msg=tfname):
                    self.test_encode_decode(tf.read())
        for msg in ["A", ""]:
            with self.subTest(msg=msg):
                self.test_encode_decode(msg)


_hidden_msgs = [
    "hidden message",
    "a",
    "",
    "\\sum_{i=0}^\\infty\\frac{1}{i!}=e",
    "Happiness is not an ideal of reason but of imagination",
]

_input_hidden = [
    ('t01', _hidden_msgs[0]),
    ('t01', _hidden_msgs[1]),
    ('t01', _hidden_msgs[2]),
    ('t01', _hidden_msgs[3]),
    ('t02', _hidden_msgs[0]),
    ('t03', _hidden_msgs[4]),
    ('t04', _hidden_msgs[4]),
]


class LZMultiCoderTest(unittest.TestCase):

    def test_encode_hide_decode(self, LZMultiCoderClass):
        for tfname, hidden_msg in _input_hidden:
            with open(os.path.join(DATA_PATH, tfname), 'r') as tf:
                msg = tf.read()
                with self.subTest(msg=(tfname, hidden_msg)):
                    lz_multi_coder = LZMultiCoderClass()
                    lz_multi_coder.start_encoding_get_capacity(msg)
                    msg_enc = lz_multi_coder.complete_encoding_hide_message(hidden_msg)
                    msg_dec, hidden_msg_dec = lz_multi_coder.decode(msg_enc)
                    self.assertEqual(msg_dec, msg)
                    self.assertEqual(hidden_msg_dec, hidden_msg)

    def test_encode_hide_decode_LZAllChoicesCoder(self):
        self.test_encode_hide_decode(LZ77AllChoicesCoder)

    def test_encode_hide_decode_LZLastTwoChoicesCoder(self):
        self.test_encode_hide_decode(LZ77LastTwoChoicesCoder)
