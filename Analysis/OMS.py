from collections import defaultdict
from DAOsAndServices import MOFDAO
limit_sample = False


def calculate_oms():
    output_lines = ['mof name, num atoms with OMS, all metal atoms with open site(s)']
    num_elements_with_open_sites = defaultdict(lambda: 0)
    num_covered = 0
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
        num_covered += 1
        if num_covered >= 2000 and limit_sample:
            break
    # create_bar_plot(presence.keys(), presence.values())
    with open("output/open_metal_sites.csv", "w") as f:
        f.write('\n'.join(output_lines))
    print(dict(num_elements_with_open_sites))


if __name__ == '__main__':
    calculate_oms()
