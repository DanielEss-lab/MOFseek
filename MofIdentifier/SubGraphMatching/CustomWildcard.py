class WC:
    def __init__(self, symbol, should_match, elements):
        self.elements = elements
        self.should_match = should_match
        self.symbol = symbol

    def __eq__(self, other):
        # return self.elements == other.elements \
        #        and self.should_match == other.should_match \
        #        and self.symbol == other.symbol
        elements_same = self.elements == other.elements
        should_same = self.should_match == other.should_match
        symbol_same = self.symbol == other.symbol
        print("compared")
        return elements_same and should_same and symbol_same

    def __str__(self):
        return f"{self.symbol} {'==' if self.should_match else '!='} {self.elements}"

    def __hash__(self):
        return str(self)

    def matches(self, element):
        if self.should_match:
            return element in self.elements
        else:  # a not was specified in creating the wildcard
            return element not in self.elements

    @classmethod
    def parse_line(cls, line):
        if '=' not in line:
            return dict()
        wildcards = dict()
        sections = line.split(';')
        for section in sections:
            section = "".join(section.split())  # remove all whitespace
            symbol, section = section.split('=')
            if section.startswith('not'):
                is_inverted = True
                section = section[3:]
            else:
                is_inverted = False
            elements = section.split(',')
            wildcard = WC(symbol, not is_inverted, elements)
            wildcards[symbol] = wildcard
        return wildcards
