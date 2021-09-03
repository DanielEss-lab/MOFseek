from pysmiles import read_smiles

from MofIdentifier.Molecules.Ligand import Ligand
from MofIdentifier.Molecules.atom import Atom

H_REPLACEMENT = 'Rpl'
WILD_REPLACEMENTS = {'*': 'Ast',
                     '%': 'Per',
                     '#': 'Pou'}
WILD_RESTORES = {v: k for k, v in WILD_REPLACEMENTS.items()}


def mol_from_file(filepath):
    with open(filepath, 'r') as file:
        line = file.readline()
    return mol_from_str(line, filepath)


def convert_smiles_to_no_h(string):
    return string.replace('H', H_REPLACEMENT)


def convert_mol_to_h(mol):
    for atom in mol.atoms:
        if atom.type_symbol == H_REPLACEMENT:
            atom.type_symbol = 'H'
            atom.label = atom.label.replace(H_REPLACEMENT, 'H')
    mol.elementsPresent['H'] = mol.elementsPresent[H_REPLACEMENT]
    mol.elementsPresent.pop(H_REPLACEMENT)


def remove_wildcards(string):
    for symbol, replacement in WILD_REPLACEMENTS.items():
        string = string.replace(symbol, replacement)
    return string


def restore_wildcards(mol):
    for atom in mol.atoms:
        if atom.type_symbol in WILD_RESTORES:
            atom.label = atom.label.replace(atom.type_symbol, WILD_RESTORES[atom.type_symbol])
            atom.type_symbol = WILD_RESTORES[atom.type_symbol]
    for replacement, symbol in WILD_RESTORES.items():
        if replacement in mol.elementsPresent:
            mol.elementsPresent[symbol] = mol.elementsPresent[replacement]
            mol.elementsPresent.pop(replacement)


def mol_from_str(string, mol_name=None):
    if mol_name is None:
        mol_name = string
    string = remove_wildcards(string)
    manually_specified_h = 'H' in string
    if manually_specified_h:
        string = convert_smiles_to_no_h(string)
    networkx_mol = networkx_graph_from_smiles(string, not manually_specified_h)
    molecule = mol_from_networkx_graph(networkx_mol, mol_name, string)
    if manually_specified_h:
        convert_mol_to_h(molecule)
    restore_wildcards(molecule)
    molecule.should_use_weak_comparison = not manually_specified_h
    return molecule


def networkx_graph_from_smiles(smiles_string, should_add_all_h_around_structure):
    return read_smiles(smiles_string, explicit_hydrogen=should_add_all_h_around_structure)


def mol_from_networkx_graph(graph, mol_name, file_string):
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
    molecule = Ligand(mol_name, list(atoms.values()), file_string)
    return molecule


if __name__ == '__main__':
    mol = mol_from_file(r'C:\Users\mdavid4\Desktop\Esslab-P66\MofIdentifier\ligands\phosphonate.smiles')
    print(mol)
    print(*mol.atoms, sep='\n')
