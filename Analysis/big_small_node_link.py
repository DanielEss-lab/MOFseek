from DAO import SBUDAO, MOFDAO


def calculate():
    biggest_nodes = list()
    biggest_node_size = 0
    smallest_nodes = list()
    biggest_linkers = list()
    biggest_linker_size = 0
    smallest_linker_size = float('inf')
    smallest_linkers = list()
    for mof_d in MOFDAO.get_mof_iterator():
        if mof_d.has_metal:
            for node in mof_d.sbu_nodes:
                size = SBUDAO.get_sbu(node.name).get_num_atoms()
                if size > biggest_node_size:
                    biggest_nodes = list()
                    biggest_node_size = size
                    biggest_nodes.append(mof_d.filename)
                elif size == biggest_node_size:
                    if len(biggest_nodes) == 0 or biggest_nodes[-1] != mof_d.filename:
                        biggest_nodes.append(mof_d.filename)
                if size <= 1:
                    if len(smallest_nodes) == 0 or smallest_nodes[-1] != mof_d.filename:
                        smallest_nodes.append(mof_d.filename)
        if mof_d.is_organic:
            for linker in mof_d.sbu_connectors:
                sbu = SBUDAO.get_sbu(linker.name)
                if 'C ' not in sbu.file_content:
                    continue
                size = sbu.get_num_atoms()
                if size == 1:
                    continue
                if size > biggest_linker_size:
                    biggest_linkers = list()
                    biggest_linker_size = size
                    biggest_linkers.append(mof_d.filename)
                elif size == biggest_linker_size:
                    if len(biggest_linkers) == 0 or biggest_linkers[-1] != mof_d.filename:
                        biggest_linkers.append(mof_d.filename)
                if size < smallest_linker_size:
                    smallest_linkers = list()
                    smallest_linker_size = size
                    smallest_linkers.append(mof_d.filename)
                elif size == smallest_linker_size:
                    if len(smallest_linkers) == 0 or smallest_linkers[-1] != mof_d.filename:
                        smallest_linkers.append(mof_d.filename)

    biggest_nodes.sort()
    smallest_nodes.sort()
    biggest_linkers.sort()
    smallest_linkers.sort()

    with open(f"output/mofs_largest_nodes.csv", "w") as f:
        f.write(f'The following have {biggest_node_size} atoms in at least one node\n')
        f.write('\n'.join(biggest_nodes))

    with open(f"output/mofs_smallest_nodes.csv", "w") as f:
        f.write(f'The following have {1} atoms in at least one node\n')
        f.write('\n'.join(smallest_nodes))

    with open(f"output/mofs_largest_linkers.csv", "w") as f:
        f.write(f'The following have {biggest_linker_size} atoms in at least one linker\n')
        f.write('\n'.join(biggest_linkers))

    with open(f"output/mofs_smallest_linkers.csv", "w") as f:
        f.write(f'The following have {smallest_linker_size} atoms in at least one linker\n')
        f.write('\n'.join(smallest_linkers))


if __name__ == '__main__':
    calculate()
