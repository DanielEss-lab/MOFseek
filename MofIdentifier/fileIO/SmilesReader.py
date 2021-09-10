from pysmiles import read_smiles

from MofIdentifier.Molecules.Ligand import Ligand
from MofIdentifier.Molecules.atom import Atom

OPEN_MARK_REPLACEMENT = 'z'
H_REPLACEMENT = 'Hh'
WILD_REPLACEMENTS = {'*': 'Aa',
                     '%': 'Pq',
                     '#': 'Py'}
WILD_RESTORES = {v: k for k, v in WILD_REPLACEMENTS.items()}

pysmiles_organic_subset = 'B C N O P S F Cl Br I * b c n o s p'.split()


def mol_from_file(filepath):
    with open(filepath, 'r') as file:
        line = file.readline()
    return mol_from_str(line, filepath)


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
        elif atom.type_symbol == H_REPLACEMENT:
            atom.label = atom.label.replace(H_REPLACEMENT, 'H')
            atom.type_symbol = 'H'
    for replacement, symbol in WILD_RESTORES.items():
        if replacement in mol.elementsPresent:
            mol.elementsPresent[symbol] = mol.elementsPresent[replacement]
            mol.elementsPresent.pop(replacement)
    if H_REPLACEMENT in mol.elementsPresent:
        mol.elementsPresent['H'] = mol.elementsPresent[H_REPLACEMENT]
        mol.elementsPresent.pop(H_REPLACEMENT)


def mol_from_str(string, mol_name=None):
    for special in WILD_REPLACEMENTS:
        if special in string:
            raise Exception(f'{special} not allowed in smiles text')
    if H_REPLACEMENT in string:
        raise Exception(f'{H_REPLACEMENT} not allowed in smiles text')
    if mol_name is None:
        mol_name = string

    original_string = string
    manually_specified_h = 'H' in original_string
    string = processable_smiles(string)

    networkx_mol = networkx_graph_from_smiles(string, not manually_specified_h)
    molecule = mol_from_networkx_graph(networkx_mol, mol_name, original_string)

    restore_wildcards(molecule)
    molecule.should_use_weak_comparison = not manually_specified_h
    return molecule


def processable_smiles(string):
    string = remove_wildcards(string)
    string = string.replace('H', H_REPLACEMENT)
    string = string.replace('`', OPEN_MARK_REPLACEMENT)  # The Smiles interpreter doesn't handle ` but does handle z
    for symbol in pysmiles_organic_subset:
        bracket_requiring_symbol = symbol + OPEN_MARK_REPLACEMENT
        string = string.replace(bracket_requiring_symbol, f"[{bracket_requiring_symbol}]")
    string = string.replace('[[', '[')
    string = string.replace(']]', ']')
    return string


def networkx_graph_from_smiles(smiles_string, should_add_all_h_around_structure):
    return read_smiles(smiles_string, explicit_hydrogen=should_add_all_h_around_structure)


def mol_from_networkx_graph(graph, mol_name, file_string):
    networkx_nodes = list(graph.nodes(data='element'))
    atoms = {}
    # make atoms
    for node in networkx_nodes:
        if str(node[1]).endswith(OPEN_MARK_REPLACEMENT):
            elem = str(node[1])[:-1]
            is_bond_limited = False
        else:
            elem = str(node[1])
            is_bond_limited = True
        name = elem + str(node[0])
        atom = Atom.without_location(name, elem)
        atom.is_bond_limited = is_bond_limited
        atoms[name] = atom
    # connect atoms
    for node in networkx_nodes:
        elem = str(node[1])[:-1] if str(node[1]).endswith(OPEN_MARK_REPLACEMENT) else str(node[1])
        name = elem + str(node[0])
        atom = atoms[name]
        for adj_node in list(graph.adj[node[0]]):
            adj = networkx_nodes[adj_node]
            adj_elem = str(adj[1])[:-1] if str(adj[1]).endswith(OPEN_MARK_REPLACEMENT) else str(adj[1])
            adj_name = adj_elem + str(adj[0])
            atom.bondedAtoms.append(atoms[adj_name])
    molecule = Ligand(mol_name, list(atoms.values()), file_string)
    return molecule


if __name__ == '__main__':
    mol = mol_from_str('[O`][P`]([O`])([O`])[O`]', 'PO4')
    print(mol)
    print(mol.atoms[0].is_bond_limited)
    print(*mol.atoms, sep='\n')
    print(mol.should_use_weak_comparison)
