from matplotlib import pyplot as plt

from DAOsAndServices import MOFDAO
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
    presence = {symbol: 0 for symbol in CovalentRadiusLookup.data}
    total_freq = {symbol: 0 for symbol in CovalentRadiusLookup.data}
    for mof in MOFDAO.get_mof_iterator():
        for element, count in mof.elements_present.items():
            presence[element] += 1
            total_freq[element] += count
    create_bar_plot(presence.keys(), presence.values())
    with open("output/element_frequency.csv", "w") as f:
        f.write('element, number of MOFs that contain element, total number of element atoms within db')
        f.write('\n'.join(f"{symbol}, {presence[symbol]}, {total_freq[symbol]}"
                          for symbol in CovalentRadiusLookup.data))
    print(total_freq)


if __name__ == '__main__':
    chart_presence()
    # plt.show()