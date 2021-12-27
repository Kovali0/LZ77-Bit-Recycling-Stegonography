from lz77_prototype.lz77_one import random_msg
import os

DATA_PATH = 'data'


def gen_input():
    alph2 = ['A', 'B']
    alph4 = ['A', 'B', 'C', 'D']
    alph_all_printable = [chr(i) for i in range(32, 127)]
    path = '..\\sample_data\\'
    with open(path + 'sampleFICT2.txt') as f:
        text1 = f.read(20000)
    with open(path + 'dickens.txt') as f:
        text2 = f.read(20000)
    test_files = [
        # Simple compression, compression + side channel
        ('t01', random_msg(alph2, 30000)),
        ('t02', random_msg(alph4, 10000)),
        ('t03', text1),
        ('t04', text2),
        # Simple compression only
        ('t05', "".join(alph_all_printable)),
        ('t06', random_msg(alph_all_printable, 1000)),
        ('t07', "A" * 200)
    ]
    for tfname, tfdata in test_files:
        with open(os.path.join(DATA_PATH, tfname), 'w') as tf:
            tf.write(tfdata)


if __name__ == '__main__':
    gen_input()

