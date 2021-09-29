from matplotlib import pyplot as plt
from collections import defaultdict

from DAO import SBUDAO
from MofIdentifier.Molecules.atom import Atom


def create_scatter_plot(x_values, y_values):
    fig, ax = plt.subplots()
    ax.scatter(x_values, y_values, s=15, marker=".", alpha=0.8)
    ax.set(ylabel='number of SBUs', xlabel='num metal atoms in SBU',
           title=f'number of metal atoms in SBU')
    ax.grid()


def chart():
    output_lines = ['node name, metal a symbol, metal a freq, metal b symbol, metal b freq, metal c symbol, '
                    'metal c freq']
    frequent_combinations = defaultdict(lambda: 0)
    for sbu in SBUDAO.get_sbu_iterator():
        sbu_object = sbu.get_sbu()
        if sbu.type != 'cluster':
            continue
        metals = {elem: freq for elem, freq in sbu_object.elementsPresent.items() if Atom.is_metal(elem)}
        if len(metals) < 2:
            continue
        sorted_symbols = list(metals.keys())
        sorted_symbols.sort()
        combination = "-".join(sorted_symbols)
        frequent_combinations[combination] += 1
        metals_string = ", ".join(f"{elem}, {freq}" for elem, freq in metals.items())
        output_lines.append(f'{sbu.name}, {metals_string}')
    y_values = frequent_combinations.keys()
    x_values = frequent_combinations.values()
    create_scatter_plot(x_values, y_values)
    with open(f"output/mixed_metals_in_nodes.csv", "w") as f:
        f.write('\n'.join(output_lines))


def num_metal(node):
    num_atoms = 0
    for atom in node.atoms:
        if atom.is_metal():
            num_atoms += 1
    return num_atoms


if __name__ == '__main__':
    chart()
    # plt.show()
