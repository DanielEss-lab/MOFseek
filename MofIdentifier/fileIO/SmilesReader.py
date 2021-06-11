from pysmiles import read_smiles

from MofIdentifier.Molecules.Ligand import Ligand
from MofIdentifier.Molecules.atom import Atom

REPLACEMENT = 'Rpl'


def mol_from_file(filepath):
    with open(filepath, 'r') as file:
        line = file.readline()
    return mol_from_str(line, filepath)


def convert_smiles_to_no_h(string):
    return string.replace('H', REPLACEMENT)


def convert_mol_to_h(mol):
    for atom in mol.atoms:
        if atom.type_symbol == REPLACEMENT:
            atom.type_symbol = 'H'
            atom.label = atom.label.replace(REPLACEMENT, 'H')
    mol.elementsPresent['H'] = mol.elementsPresent[REPLACEMENT]
    mol.elementsPresent.pop(REPLACEMENT)


def mol_from_str(string, mol_name=None):
    if mol_name is None:
        mol_name = string
    manually_specified_h = 'H' in string
    if manually_specified_h:
        string = convert_smiles_to_no_h(string)
    networkx_mol = networkx_graph_from_smiles(string, not manually_specified_h)
    molecule = mol_from_networkx_graph(networkx_mol, mol_name)
    if manually_specified_h:
        convert_mol_to_h(molecule)
    molecule.should_use_weak_comparison = not manually_specified_h
    return molecule


def networkx_graph_from_smiles(smiles_string, should_add_all_h_around_structure):
    return read_smiles(smiles_string, explicit_hydrogen=should_add_all_h_around_structure)


def mol_from_networkx_graph(graph, mol_name):
    networkx_nodes = list(graph.nodes(data='element'))
    atoms = {}
    for node in networkx_nodes:
        name = str(node[1]) + str(node[0])
        atoms[name] = Atom.without_location(str(name), str(node[1]))
    for node in networkx_nodes:
        name = str(node[1]) + str(node[0])
        atom = atoms[name]
        for adj_node in list(graph.adj[node[0]]):
            adj = networkx_nodes[adj_node]
            adj_name = str(adj[1]) + str(adj[0])
            atom.bondedAtoms.append(atoms[adj_name])
    molecule = Ligand(mol_name, list(atoms.values()))
    return molecule


if __name__ == '__main__':
    mol = mol_from_str('[H]C1=C([H])C([H])=C([H])C([H])=C1[H]')
    print(mol)
    print(*mol.atoms, sep='\n')
