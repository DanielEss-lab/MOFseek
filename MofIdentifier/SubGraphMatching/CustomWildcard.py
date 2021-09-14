class WC:
    def __init__(self, symbol, should_match, elements):
        self.elements = elements
        self.should_match = should_match
        self.symbol = symbol

    def __eq__(self, other):
        return self.elements == other.elements \
               and self.should_match == other.should_match \
               and self.symbol == other.symbol

    def matches(self, element):
        if self.should_match:
            return element in self.elements
        else:  # a not was specified in creating the wildcard
            return element not in self.elements

    @classmethod
    def parse_line(cls, line):
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
