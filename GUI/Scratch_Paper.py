def to_sup(s):
    sups = {u'0': u'\u2070',
            u'1': u'\xb9',
            u'2': u'\xb2',
            u'3': u'\xb3',
            u'4': u'\u2074',
            u'5': u'\u2075',
            u'6': u'\u2076',
            u'7': u'\u2077',
            u'8': u'\u2078',
            u'9': u'\u2079'}

    return ''.join(sups.get(char, char) for char in s)  # lose the list comprehension


SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")


def to_sub(s):
    return s.translate(SUB)


if __name__ == '__main__':
    test_strings= ['0123456789', 'C', '12 C', 'C12']
    print(*[to_sub(string) for string in test_strings])
