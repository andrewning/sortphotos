"""
Misc utilities.
"""

def make_string(seq):
    """
    Don't throw an exception when given an out of range character.
    """
    string = ''
    for c in seq:
        # Screen out non-printing characters
        if 32 <= c and c < 256:
            string += chr(c)
    # If no printing chars
    if not string:
        return str(seq)
    return string


def make_string_uc(seq):
    """
    Special version to deal with the code in the first 8 bytes of a user comment.
    First 8 bytes gives coding system e.g. ASCII vs. JIS vs Unicode.
    """
    #code = seq[0:8]
    seq = seq[8:]
    # Of course, this is only correct if ASCII, and the standard explicitly
    # allows JIS and Unicode.
    return make_string( make_string(seq) )


def s2n_motorola(str):
    """Extract multibyte integer in Motorola format (little endian)."""
    x = 0
    for c in str:
        x = (x << 8) | ord(c)
    return x


def s2n_intel(str):
    """Extract multibyte integer in Intel format (big endian)."""
    x = 0
    y = 0
    for c in str:
        x = x | (ord(c) << y)
        y = y + 8
    return x


class Ratio:
    """
    Ratio object that eventually will be able to reduce itself to lowest
    common denominator for printing.
    """
    def __init__(self, num, den):
        self.num = num
        self.den = den

    def __repr__(self):
        self.reduce()
        if self.den == 1:
            return str(self.num)
        return '%d/%d' % (self.num, self.den)

    def _gcd(self, a, b):
        if b == 0:
            return a
        else:
            return self._gcd(b, a % b)

    def reduce(self):
        div = self._gcd(self.num, self.den)
        if div > 1:
            self.num = self.num // div
            self.den = self.den // div

