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
    output_lines = ['mof name, num atoms with OMS, all metal atoms with open site(s)']
    num_elements_with_open_sites = defaultdict(lambda: 0)
    for mof_d in MOFDAO.get_mof_iterator():
        mof = mof_d.get_mof()
        if len(mof.open_metal_sites) == 0:
            output_lines.append(f'{mof.label}, no open metal sites detected')
        else:
            output_lines.append(f'{mof.label}, {len(mof.open_metal_sites)}, '
                                f'{" ".join([atom.label for atom in mof.open_metal_sites])}')
        elements_open = set()
        for atom in mof.open_metal_sites:
            elements_open.add(atom.type_symbol)
        num_elements_with_open_sites[len(elements_open)] += 1
    # create_bar_plot(presence.keys(), presence.values())
    with open("output/open_metal_sites.csv", "w") as f:
        f.write('\n'.join(output_lines))
    print(dict(num_elements_with_open_sites))


if __name__ == '__main__':
    chart_oms()
    # plt.show()
