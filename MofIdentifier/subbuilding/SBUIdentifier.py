import MofIdentifier
from MofIdentifier.bondTools import Distances
from MofIdentifier.fileIO import XyzWriter
from MofIdentifier.subbuilding.SBUTools import SBUCollection, changeableSBU, UnitType


def split(mof, show_duplicates=False, aux_as_part_of_node=False):
    identifier = SBUIdentifier(mof, show_duplicates)
    return identifier.run_algorithm()


def mof_has_all_sbus(mof, sbus):
    if all(sbu in mof.sbus().all() for sbu in sbus):
        return True
    return False


def mof_has_no_sbus(mof, sbus):
    if any(sbu in mof.sbus().all() for sbu in sbus):
        return False
    return True


def reduce_duplicates(sbu_list, is_duplicate):
    sbu_list = sbu_list.copy()
    new_sbu_list = list()
    i = 0
    while i < len(sbu_list):
        new_sbu_list.append(sbu_list[i])
        j = i + 1
        while j < len(sbu_list):
            if is_duplicate(sbu_list[i], sbu_list[j]):
                new_sbu_list[i].frequency += sbu_list[j].frequency
                sbu_list.pop(j)
            else:
                j += 1
        i += 1
    return new_sbu_list


def check_for_infinite_band(sbu_atoms):
    # If any molecule can traverse the cluster or connector and get to itself by crossing cell boundary
    # panes an odd number of times, then all molecules can, and then they are an infinite band.
    for starting_atom in sbu_atoms:
        if len(in_sbu_neighbors(starting_atom, sbu_atoms)) > 1:  # If it only has one neighbor, algorithm won't work
            if check_for_inf_recurse(sbu_atoms, set(), starting_atom, starting_atom, 0):
                return True
    return False


def in_sbu_neighbors(atom, sbu_atoms):
    return [neighbor for neighbor in atom.bondedAtoms if neighbor in sbu_atoms]


def check_for_inf_recurse(sbu_atoms, visited, target_atom, atom, panes_crossed):
    visited.add(atom)
    for neighbor in in_sbu_neighbors(atom, sbu_atoms):
        if neighbor == target_atom and panes_crossed + panes_crossed_in_bond(atom, neighbor) % 2 == 1:
            # if panes_crossed (plus possible pane in traversal from atom to neighbor) is odd:
            return True
        if neighbor not in visited:
            crosses_pane = panes_crossed_in_bond(atom, neighbor)
            if check_for_inf_recurse(sbu_atoms, visited, target_atom, neighbor, panes_crossed + crosses_pane):
                return True
    return False


def panes_crossed_in_bond(a, b):
    atom_1, atom_2 = a, b
    while not atom_1.is_in_unit_cell():
        atom_1 = atom_1.original
    while not atom_2.is_in_unit_cell():
        atom_2 = atom_2.original
    if Distances.are_within_bond_range(atom_1, atom_2):
        return 0  # only works on MOFS with unit cell lengths > 8ish; I hope that's not a problem
    num_panes = 0
    if atom_2.a - atom_1.a > 0.5 or atom_2.a - atom_1.a < -0.5:
        num_panes += 1
    if atom_2.b - atom_1.b > 0.5 or atom_2.b - atom_1.b < -0.5:
        num_panes += 1
    if atom_2.c - atom_1.c > 0.5 or atom_2.c - atom_1.c < -0.5:
        num_panes += 1
    return num_panes


def panes_between(start, end, cluster):
    _, panes = panes_between_recurse(start, end, set(), 0, cluster)
    assert panes is not None
    return panes


def panes_between_recurse(atom, end, visited, num_panes, cluster):
    if atom == end:
        return True, num_panes
    visited.add(atom)
    for neighbor in atom.bondedAtoms:
        if neighbor in cluster.atoms:  # Only look within the cluster
            if neighbor not in visited:
                crosses_pane = panes_crossed_in_bond(atom, neighbor)
                found_end, panes = panes_between_recurse(neighbor, end, visited, num_panes + crosses_pane, cluster)
                if found_end:
                    return found_end, panes
    return False, None


class SBUIdentifier:
    def __init__(self, mof, show_duplicates):
        self.atoms = mof.atoms
        self.mof = mof
        self.atom_to_SBU = dict()
        self.next_group_id = 1
        self.groups = dict()
        self.allow_two_steps = True
        self.show_duplicates = show_duplicates

    def been_visited(self, atom):
        return atom.label in self.atom_to_SBU

    def mark_group(self, atom, group_id):
        self.atom_to_SBU[atom.label] = group_id

    def group_id_of(self, atom):
        return self.atom_to_SBU[atom.label]

    def run_algorithm(self):
        clusters = list(())
        connectors = list(())
        auxiliaries = list(())
        for atom in self.atoms:
            if MofIdentifier.Molecules.atom.is_metal(atom.type_symbol) and not self.been_visited(atom):
                sbu = self.identify_cluster(atom)
                if sbu.frequency == float('inf') and self.allow_two_steps:
                    # Try algorithm again, from the top, but with stricter cluster definition
                    identifier = SBUIdentifier.copy_from(self)
                    identifier.allow_two_steps = False
                    return identifier.run_algorithm()
                else:
                    clusters.append(sbu)
                    self.groups[self.next_group_id] = sbu
                    self.next_group_id += 1
        if len(clusters) == 0:
            raise Exception(f'Exiting algorithm early because no metal atoms found for mof {self.mof.label}')
        for atom in self.atoms:
            if not self.been_visited(atom):
                if self.successfully_adds_to_cluster(atom):
                    continue
                sbu = self.identify_ligand(atom)
                self.groups[self.next_group_id] = sbu
                if sbu.type == UnitType.CONNECTOR:
                    connectors.append(sbu)
                else:
                    auxiliaries.append(sbu)
                self.next_group_id += 1
        for cluster in clusters:
            self.set_adj_ids(cluster)
        if not self.show_duplicates:
            clusters = reduce_duplicates(clusters, lambda x, y: x == y)
            connectors = reduce_duplicates(connectors, lambda x, y: x == y)
            auxiliaries = reduce_duplicates(auxiliaries, lambda x, y: x == y)
        for sbu in clusters + connectors + auxiliaries:
            sbu.normalize_atoms(self.mof)
            sbu.file_content = XyzWriter.atoms_to_xyz_string(sbu.atoms, '')
        return SBUCollection(clusters, connectors, auxiliaries)

    def identify_cluster(self, metal_atom):
        atoms = set()
        self.identify_cluster_recurse(metal_atom, atoms)
        if check_for_infinite_band(atoms):
            return changeableSBU(self.next_group_id, UnitType.CLUSTER, atoms, float('inf'))
        else:
            return changeableSBU(self.next_group_id, UnitType.CLUSTER, atoms)

    def identify_cluster_recurse(self, metal_atom, atoms):
        atoms.add(metal_atom)
        self.mark_group(metal_atom, self.next_group_id)
        for neighbor in metal_atom.bondedAtoms:
            if MofIdentifier.Molecules.atom.is_metal(neighbor.type_symbol) and not self.been_visited(neighbor):
                self.identify_cluster_recurse(neighbor, atoms)
        # The following section helps to identify more complex nodes by including metal atoms two steps away
        # It does this only when the intermediate molecule (usually Oxygen) ONLY connects to metals.
        if self.allow_two_steps:
            for neighbor in metal_atom.bondedAtoms:
                self.check_for_including_distant_metals(neighbor, atoms)

    def check_for_including_distant_metals(self, possible_in_node_link, atoms):
        if not self.been_visited(possible_in_node_link):
            has_been_added = False
            for second_neighbor in possible_in_node_link.bondedAtoms:
                if not MofIdentifier.Molecules.atom.is_metal(second_neighbor.type_symbol):
                    return
            for second_neighbor in possible_in_node_link.bondedAtoms:
                if second_neighbor not in atoms:
                    if not has_been_added:
                        atoms.add(possible_in_node_link)
                        self.mark_group(possible_in_node_link, self.next_group_id)
                        has_been_added = True
                    self.identify_cluster_recurse(second_neighbor, atoms)

    def identify_ligand(self, nonmetal_atom):
        atoms = set()
        adjacent_cluster_ids = set()
        self.identify_ligand_recurse(nonmetal_atom, atoms, adjacent_cluster_ids)
        self.correct_adjacent_cluster_ids(atoms, adjacent_cluster_ids)
        if len(adjacent_cluster_ids) > 1:
            ligand_type = UnitType.CONNECTOR
        else:
            ligand_type = UnitType.AUXILIARY
        if check_for_infinite_band(atoms):
            return changeableSBU(self.next_group_id, ligand_type, atoms, float('inf'), adjacent_cluster_ids)
        else:
            return changeableSBU(self.next_group_id, ligand_type, atoms, 1, adjacent_cluster_ids)

    def identify_ligand_recurse(self, nonmetal_atom, ligand_atoms, adjacent_cluster_ids):
        ligand_atoms.add(nonmetal_atom)
        self.mark_group(nonmetal_atom, self.next_group_id)
        for neighbor in nonmetal_atom.bondedAtoms:
            if not self.been_visited(neighbor):
                self.identify_ligand_recurse(neighbor, ligand_atoms, adjacent_cluster_ids)
            elif MofIdentifier.Molecules.atom.is_metal(neighbor.type_symbol):
                adjacent_cluster_ids.add(self.group_id_of(neighbor))

    def successfully_adds_to_cluster(self, atom):
        num_cluster_neighbors = 0
        num_noncluster_neighbors = 0
        cluster_ids = set()
        cluster = None
        for neighbor in atom.bondedAtoms:
            if self.been_visited(neighbor):
                cluster = self.groups[self.group_id_of(neighbor)]
                if cluster.type == UnitType.CLUSTER:
                    num_cluster_neighbors += 1
                    cluster_ids.add(cluster.sbu_id)
                else:
                    num_noncluster_neighbors += 1  # TODO: clarify in comment when this scenario occurs
            else:
                num_noncluster_neighbors += 1
        if atom.type_symbol == 'H':
            assert len(atom.bondedAtoms) <= 1
            for neighbor in atom.bondedAtoms:
                if self.successfully_adds_to_cluster(neighbor):
                    cluster = self.groups[self.group_id_of(neighbor)]
                    cluster.add_atom(atom)
                    self.mark_group(atom, cluster.sbu_id)
                    return True
        if atom.type_symbol == 'O' and len(atom.bondedAtoms) == 1:
            for neighbor in atom.bondedAtoms:
                if neighbor.is_metal():
                    return False
        if num_cluster_neighbors > 1 + num_noncluster_neighbors and len(cluster_ids) == 1:
            # if num_noncluster_neighbors == 1 then it's likely to be part of an aux sbu, not part of the cluster
            cluster.add_atom(atom)
            self.mark_group(atom, cluster.sbu_id)
            return True
        return False

    def set_adj_ids(self, cluster):
        for atom in cluster.atoms:
            for neighbor in atom.bondedAtoms:
                neighbor_id = self.group_id_of(neighbor)
                if neighbor_id != cluster.sbu_id:
                    if self.groups[neighbor_id].type == UnitType.CONNECTOR:
                        cluster.adjacent_connector_ids.add(neighbor_id)
                    else:
                        cluster.adjacent_auxiliary_ids.add(neighbor_id)

    def correct_adjacent_recurse(self, ligand_atoms, adjacent_cluster_ids, visited, num_panes_to_neighbor,
                                 atom, panes_crossed, representative_atom_of_cluster):
        visited.add(atom)
        for neighbor in atom.bondedAtoms:
            if neighbor in ligand_atoms:
                if neighbor not in visited:
                    crosses_pane = panes_crossed_in_bond(atom, neighbor)
                    self.correct_adjacent_recurse(ligand_atoms, adjacent_cluster_ids, visited, num_panes_to_neighbor,
                                                  neighbor, panes_crossed+crosses_pane, representative_atom_of_cluster)
            else:  # must belong to a cluster
                cluster_id = self.atom_to_SBU[neighbor.label]
                if cluster_id in representative_atom_of_cluster:
                    repr_atom = representative_atom_of_cluster[cluster_id]
                    num_panes_to_repr_atom = panes_between(neighbor, repr_atom, self.groups[cluster_id]) \
                        + panes_crossed + panes_crossed_in_bond(atom, neighbor)
                    if abs(num_panes_to_repr_atom - num_panes_to_neighbor[repr_atom.label]) % 2 == 1:  # Off by 1,3,etc
                        adjacent_cluster_ids.add(-1 * cluster_id)
                else:
                    representative_atom_of_cluster[cluster_id] = neighbor
                    panes_crossed_to_neighbor = panes_crossed + panes_crossed_in_bond(atom, neighbor)
                    num_panes_to_neighbor[neighbor.label] = panes_crossed_to_neighbor

    def correct_adjacent_cluster_ids(self, ligand_atoms, adjacent_cluster_ids):
        # If it can touch an atom (ie part of a cluster) by going through both odd and even numbers of panes,
        # then it actually touches that atom twice, in two different copies of the unit cell- so, another connection
        for starting_atom in ligand_atoms:
            self.correct_adjacent_recurse(ligand_atoms, adjacent_cluster_ids, set(), dict(), starting_atom, 0, dict())
            break

    @classmethod
    def copy_from(cls, other):
        return SBUIdentifier(other.mof, other.show_duplicates)
