from matplotlib import pyplot as plt

from DAO import SBUDAO


def create_scatter_plot(x_values, y_values, type_name):
    fig, ax = plt.subplots()
    ax.scatter(x_values, y_values, s=15, marker=".", alpha=0.8)
    ax.set(xlabel='number of SBUs', ylabel='num atoms in SBU',
           title=f'{type_name} sizes')
    ax.grid()


def chart_type(type_name):
    num_sbus_by_size = dict()
    for sbu in SBUDAO.get_sbu_iterator():
        if sbu.type == type_name:
            sbu_object = sbu.get_sbu()
            if len(sbu_object.atoms) in num_sbus_by_size:
                num_sbus_by_size[len(sbu_object.atoms)] += 1
            else:
                num_sbus_by_size[len(sbu_object.atoms)] = 1
    x_values = num_sbus_by_size.keys()
    y_values = num_sbus_by_size.values()
    create_scatter_plot(x_values, y_values, type_name)


if __name__ == '__main__':
    chart_type('cluster')
    chart_type('connector')
    plt.show()
