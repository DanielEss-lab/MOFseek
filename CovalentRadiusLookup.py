class CovalentRadiusLookup:
    def __init__(self):
        self.data = dict(())
        # https://chem.libretexts.org/Ancillary_Materials/Reference/Reference_Tables/Atomic_and_Molecular_Properties/A3%3A_Covalent_Radii
        with open('radiusChart.txt', 'r') as chart:
            for line in chart:
                pieces = line.split()
                if pieces[2] == '-':
                    radius = pieces[3]
                else:
                    radius = max(float(pieces[2]), float(pieces[3]))
                symbol = pieces[1]
                self.data[symbol] = radius

    def lookup(self, symbol):
        return self.data[symbol]/100


if __name__ == '__main__':
    # uses https://pypi.org/project/PyCifRW/4.3/#description to read CIF files
    chart = CovalentRadiusLookup()
    radii = chart.lookup('C')
    print(radii)
