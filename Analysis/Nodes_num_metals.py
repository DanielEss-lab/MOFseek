from matplotlib import pyplot as plt
from collections import defaultdict

from DAO import SBUDAO


def create_scatter_plot(x_values, y_values):
    fig, ax = plt.subplots()
    ax.scatter(x_values, y_values, s=15, marker=".", alpha=0.8)
    ax.set(ylabel='number of SBUs', xlabel='num metal atoms in SBU',
           title=f'number of metal atoms in SBU')
    ax.grid()


def chart():
    output_lines = ['node name, number of metal atoms']
    num_sbus_by_num_metal = defaultdict(lambda: 0)
    num_c = 0
    for sbu in SBUDAO.get_sbu_iterator():
        num_c += 1
        if sbu.type == 'cluster':
            print(sbu.name)
            sbu_object = sbu.get_sbu()
            m_atoms = num_metal(sbu_object)
            num_sbus_by_num_metal[m_atoms] += 1
            output_lines.append(f'{sbu.name}, {m_atoms}')
    y_values = num_sbus_by_num_metal.keys()
    x_values = num_sbus_by_num_metal.values()
    print(num_c)
    create_scatter_plot(y_values, x_values)
    with open(f"output/cluster_num_metals.csv", "w") as f:
        f.write('\n'.join(output_lines))


def num_metal(node):
    num_atoms = 0
    for atom in node.atoms:
        if atom.is_metal():
            num_atoms += 1
    return num_atoms


if __name__ == '__main__':
    chart()
    plt.show()
