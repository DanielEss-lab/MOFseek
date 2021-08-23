from matplotlib import pyplot as plt

from DAO import MOFDAO
from MofIdentifier.bondTools import CovalentRadiusLookup


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


def chart_presence():
    freq = {symbol: 0 for symbol in CovalentRadiusLookup.data}
    for mof in MOFDAO.get_mof_iterator():
        for element in mof.elements_present:
            freq[element] += 1
    create_bar_plot(freq.keys(), freq.values())


if __name__ == '__main__':
    chart_presence()
    plt.show()