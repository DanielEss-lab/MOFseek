from pathlib import Path

data = dict(())
# https://chem.libretexts.org/Ancillary_Materials/Reference/Reference_Tables/Atomic_and_Molecular_Properties/A3%3A_Covalent_Radii
path = Path(__file__).parent / "radiusChart.txt"
with path.open() as chart:
    for line in chart:
        pieces = line.split()
        if pieces[2] == '-':
            radius = pieces[3]
        else:
            radius = max(float(pieces[2]), float(pieces[3]))
        symbol = pieces[1]
        data[symbol] = radius


def lookup(symbol):
    if symbol == '#':
        return 1.1
    elif symbol == '*':
        return 1.7
    elif symbol == '%':
        return 1.7
    else:
        return data[symbol] / 100


if __name__ == '__main__':
    radius_1 = lookup('H')
    radius_2 = lookup('N')
    print((radius_1 + radius_2) * 1.10 + 0.05)
