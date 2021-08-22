"""Huffman entropy coding."""


class HuffmanTreeNode:
    """
    Class representing a node of the Huffman symbol-code tree
    """

    def __init__(self, symbol, cnt, left=None, right=None):
        self.symbol = symbol
        self.cnt = cnt
        self.left = left
        self.right = right

    def __eq__(self, other):
        return self.symbol == other.symbol and self.cnt == other.cnt

    def print(self, offset=""):
        is_leaf = "<leaf>" if self.is_leaf() else ""
        print(f"{offset}({self.symbol}, {self.cnt}){is_leaf}")
        if self.left:
            self.left.print(offset + "--")
        if self.right:
            self.right.print(offset + "--")

    def is_leaf(self):
        return not (self.left and self.right)


def insert_sorted(seq, obj, key=lambda x: x, desc=False):
    """Inserts an object into sorted iterable sequence"""
    if desc:
        cmp = lambda a, b: a > b
    else:
        cmp = lambda a, b: a < b
    idx = 0
    # Guard element at the end
    seq.append(obj)
    while cmp(key(seq[idx]), key(obj)):
        idx += 1
    seq.insert(idx, obj)
    # Remove the guard
    seq.pop()


class SimpleHuffmanCoder:

    @staticmethod
    def symbol_frequencies(string):
        """Counts frequencies of all string symbols
        :returns dictionary {[character]: [count]})"""
        symbol_freq = dict()
        for c in string:
            if c not in symbol_freq:
                symbol_freq[c] = 1
            else:
                symbol_freq[c] += 1
        return symbol_freq

    def __init__(self, string=None):
        # Tree of symbol code-structure
        self._symbol_tree = None
        # Dictionary of symbol binary codes
        self._code_dict = dict()
        if string:
            self.fit(string)

    def fit(self, symbol_frequency):
        """:param symbol_frequency: dict(str, int)"""
        self._make_code_tree(symbol_frequency)
        self._make_code_dict()

    def _make_code_tree(self, symbols_frequencies):
        """Creates inner symbol-code tree according to symbols and their frequencies"""
        # Make a symbol-frequency list, sort by the second element (count)
        symbol_freq_arr = sorted(symbols_frequencies.items(), key=lambda x: x[1], reverse=True)
        # Construct the symbol-code tree
        symbol_nodes = [HuffmanTreeNode(s, cnt) for (s, cnt) in symbol_freq_arr]
        while len(symbol_nodes) > 1:
            # Couple the two last elements into a new tree node
            node1 = symbol_nodes.pop()
            node2 = symbol_nodes.pop()
            # Create the parent symbol node
            node_parent = HuffmanTreeNode(node1.symbol + node2.symbol, node1.cnt + node2.cnt,
                                          left=node1, right=node2)
            # Insert new tree node at correct position (sorted)
            insert_sorted(symbol_nodes, node_parent, key=lambda x: x.cnt, desc=True)
        self._symbol_tree = symbol_nodes[0]

    def _make_code_dict(self):
        """Creates symbol-code dictionary from the symbol tree"""
        def code_node(node, cur_code):
            # The node is a leaf - assign code
            if node.is_leaf():
                self._code_dict[node.symbol] = cur_code
            else:
                # Repeat for children
                code_node(node.left, cur_code + '0')
                code_node(node.right, cur_code + '1')
        # Start coding for the tree root
        code_node(self._symbol_tree, '')

    def encode(self, string):
        code_string = [self._code_dict[symbol] for symbol in string]
        return "".join(code_string)

    def decode(self, string):
        symbol_node = self._symbol_tree
        string_decoded = ""
        for bit in string:
            if bit == '0':
                symbol_node = symbol_node.left
            elif bit == '1':
                symbol_node = symbol_node.right
            else:
                raise ValueError(f'Unexpected non-binary symbol in the string to decode: {bit}')
            if symbol_node.is_leaf():
                string_decoded += symbol_node.symbol
                symbol_node = self._symbol_tree
        return string_decoded


class CanonicalHuffmanCoder(SimpleHuffmanCoder):
    """
    Improved Huffman coder - reduced data (message) header, faster decoding
    """
    def __init__(self, string=None):
        self._symbol_code_lengths = dict()
        self._symbol_code_arr = None
        super().__init__(string)

    def fit(self, symbol_frequency):
        """
        Fits the coder to the distribution of symbols of a sample data in order
        to encode it optimally.
        :param symbol_frequency: dictionary of symbols and their frequencies {<symbol>: <freq>}
        """
        self._make_code_tree(symbol_frequency)
        self._make_code_dict()
        for symbol, code in self._code_dict.items():
            self._symbol_code_lengths[symbol] = len(code)
        self._make_canonical_dict(self._symbol_code_lengths)

    def _make_canonical_dict(self, symbol_code_lengths):
        """Creates "canonical" dictionary with properly sorted codes
        :param symbol_code_lengths: a dictionary that says how long is the
         code for each symbol {<symbol>: <code length>}"""
        self._symbol_code_arr = list(symbol_code_lengths.items())
        # Sort pairs of by code lengths, then by symbols
        self._symbol_code_arr = sorted(self._symbol_code_arr, key=lambda x: (x[1], x[0]))
        # First code - zeros
        new_code = '0' * self._symbol_code_arr[0][1]
        self._symbol_code_arr[0] = (self._symbol_code_arr[0][0], new_code)
        for i in range(1, len(self._symbol_code_arr)):
            # Generate new code - increment and adjust length
            new_code_val = int(new_code, 2) + 1
            new_code = bin(new_code_val)[2:].zfill(len(new_code))
            if self._symbol_code_arr[i][1] > len(new_code):
                new_code += '0'
            self._symbol_code_arr[i] = (self._symbol_code_arr[i][0], new_code)
        # Update the code dictionary
        self._code_dict = dict(self._symbol_code_arr)

    def encode(self, string) -> tuple:
        """Encodes a string to the binary code and symbol-code_length list
        :returns: (encoded_string, code_lengths)"""
        string_enc = super().encode(string)
        # code_lengths = [(symbol, len(code)) for (symbol, code) in self._code_dict.items()]
        return string_enc, self._symbol_code_lengths

    def decode(self, string, code_lengths) -> str:
        """
        Decodes a previously encoded string.
        :param string: encoded message, string of bits
        :param code_lengths: dictionary {<symbol>:<code length>}
        :returns: decoded message, string
        """
        # Generate canonical codes
        self._make_canonical_dict(code_lengths)

        # TODO: handle multi-character symbols (like '-a'->'0100') - below

        # Get maximum code length
        # max_length = max(self._symbol_code_arr, key=lambda x: len(x[1]))
        max_length = len(self._symbol_code_arr[-1][1])
        # Make extended code-symbol table
        all_codes = ""
        for symbol, code in self._symbol_code_arr:
            # Number of extra suffixes to this code
            n_suffixes = 2 ** (max_length - len(code))
            all_codes += symbol * n_suffixes
        string_dec = ""
        while string:
            code = string[:max_length]
            # Correction for the last several codes
            if len(code) < max_length:
                code += '0' * (max_length-len(code))
            symbol_dec = all_codes[int(code, 2)]
            string_dec += symbol_dec
            string = string[code_lengths[symbol_dec]:]
        return string_dec


if __name__ == '__main__':
    # text = "a" * 20 + "b" * 15 + "c" * 12 + "d" * 7 + "e" * 5
    # text = 'a'*15+'b'*7+'c'*6+'d'*6+'e'*5
    # text = 'a'*6 + 'b'*4 + 'c'*3 + 'd'*2
    text = "But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I " \
    "will give you a complete account of the system, and expound the actual teachings of the great explorer of the " \
    "truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is " \
    "pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are " \
    "extremely painful. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, " \
    "because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some " \
    "great pleasure. To take a trivial example, which of us ever undertakes laborious physical exercise, " \
    "except to obtain some advantage from it? But who has any right to find fault with a man who chooses to enjoy a " \
    "pleasure that has no annoying consequences, or one who avoids a pain that produces no resultant pleasure? "

    text1 = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore " \
                 "et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut " \
                 "aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse " \
                 "cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, " \
                 "sunt in culpa qui officia deserunt mollit anim id est laborum "
    sample = "Lorem"
    print("Input:\n", text, "\n")
    coder_in = CanonicalHuffmanCoder(text)
    # print("Coder symbol tree:")
    # huff_coder._symbol_tree.print()
    # print("Coder dictionary:")
    # code_dict = huff_coder._code_dict
    # code_lengths = dict()
    # for s, code in code_dict.items():
    #     ln = len(code)
    #     if ln not in code_lengths:
    #         code_lengths[ln] = s
    #     else:
    #         code_lengths[ln] += s
    # for k in code_lengths.keys():
    #     code_lengths[k] = ''.join(sorted(code_lengths[k]))
    # print("Code lengths of symbols:", code_lengths)
    text_enc, lengths = coder_in.encode(text)
    print("Encoded:\n", text_enc)
    print("Symbol code lengths:\n", lengths, "\n")
    coder_out = CanonicalHuffmanCoder()
    text_dec = coder_out.decode(text_enc, lengths)
    print("Decoded:\n", text_dec, "\n")
    if text == text_dec:
        print("CODING CORRECT")
    else:
        print("SOMETHING WENT WRONG!")
    print("Input length:", len(text), "bytes")
    len_enc = len(text_enc) // 8
    print("Encoded length:", len_enc, "bytes")
    print("Compression ratio:", len_enc / len(text))