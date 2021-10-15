from collections import defaultdict

from matplotlib import pyplot as plt

from DAO import MOFDAO
from MofIdentifier.bondTools import CovalentRadiusLookup, OpenMetalSites


def create_bar_plot(x_values, y_values):
    x_numbers = [2.0 * x for x in range(len(x_values))]
    fig = plt.figure(figsize=(20, 4))
    ax = fig.add_subplot(111)
    ax.bar(x_numbers, y_values, 1.4, log=True)
    ax.set(xlabel='element symbol', ylabel='number of MOFs in which element is present',
           title=f'Element frequencies in database')
    ax.set_xticks(x_numbers)
    ax.set_xticklabels(x_values)
    for item in (ax.get_xticklabels()):
        item.set_fontsize(7)
    # ax.grid()


def chart_oms():
    output_lines = ['mof name, example OMS atom, example OMS atom bond number, example OMS atom distance from center of position, all metal atoms with open site']
    num_elements_with_open_sites = defaultdict(lambda: 0)
    for mof_d in MOFDAO.get_mof_iterator():
        mof = mof_d.get_mof()
        atoms_with_oms, example_atom, example_num_bonds, example_d = OpenMetalSites.process(mof, True)
        output_lines.append(f'{mof.label}, {example_atom.label}, {example_num_bonds}, {example_d}, {atoms_with_oms}')
        elements_open = set()
        for atom in atoms_with_oms:
            elements_open.add(atom.type_symbol)
        num_elements_with_open_sites[len(elements_open)] += 1
    # create_bar_plot(presence.keys(), presence.values())
    with open("output/open_metal_sites.csv", "w") as f:
        f.write('\n'.join(output_lines))
    print(num_elements_with_open_sites)


if __name__ == '__main__':
    chart_oms()
    # plt.show()