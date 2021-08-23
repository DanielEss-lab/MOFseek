from matplotlib import pyplot as plt

from DAO import SBUDAO


def create_scatter_plot(x_values, y_values, type_name):
    fig, ax = plt.subplots()
    ax.scatter(x_values, y_values, s=15, marker=".", alpha=0.8)
    ax.set(xlabel='frequency within database', ylabel='num separate SBUs with frequency',
           title=f'{type_name} frequency')
    ax.grid()

def chart_type(type_name):
    num_sbus_by_freq = dict()
    for sbu in SBUDAO.get_sbu_iterator():
        if sbu.type == type_name:
            if sbu.frequency in num_sbus_by_freq:
                num_sbus_by_freq[sbu.frequency] += 1
            else:
                num_sbus_by_freq[sbu.frequency] = 1
    x_values = num_sbus_by_freq.keys()
    y_values = num_sbus_by_freq.values()
    create_scatter_plot(x_values, y_values, type_name)

if __name__ == '__main__':
    chart_type('cluster')
    chart_type('connector')
    plt.show()