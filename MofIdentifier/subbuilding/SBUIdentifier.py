import collections

import MofIdentifier
import copy
from collections import deque
from MofIdentifier.Molecules import Atom
from MofIdentifier.SubGraphMatching import SubGraphMatcher
from MofIdentifier.bondTools import Distances, CovalentRadiusLookup
from MofIdentifier.fileIO import XyzWriter
from MofIdentifier.subbuilding.SBUTools import SBUCollection, changeableSBU, UnitType


class InfiniteBandWithTwoStepFindingException(Exception):
    pass


def split(mof, show_duplicates=False, check_to_modify_bonds=False):
    identifier = SBUIdentifier(mof, show_duplicates, check_to_modify_bonds)
    try:
        return identifier.run_algorithm()
    except InfiniteBandWithTwoStepFindingException:
        stricter_identifier = SBUIdentifier.copy_from(identifier)
        stricter_identifier.allow_two_steps = False
        return stricter_identifier.run_algorithm()


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
        new_sbu_list.append(copy.copy(sbu_list[i]))
        j = i + 1
        while j < len(sbu_list):
            if is_duplicate(sbu_list[i], sbu_list[j]):
                new_sbu_list[i].frequency += sbu_list[j].frequency
                sbu_list.pop(j)
            else:
                j += 1
        i += 1
    return new_sbu_list


def is_infinite_band(sbu_atoms):
    # Imagine the walls of the unit cell as panes through which atoms bond. If any atom can connect, through any
    # number of bonds, to an atom in its own cluster by going through paths with different numbers of panes,
    # then it actually touches that atom twice, in two different copies of the unit cell- so, the cluster extends
    # infinitely in at least one direction, and might be a metal line or metal pole rather than a single metal node.
    starting_atom = None
    for atom in sbu_atoms:
        # print(atom)
        starting_atom = atom
        break
    panes_in_path = {starting_atom: PanesCrossed()}  # default PanesCrossed is 0 panes
    explore_queue = collections.deque()
    explore_queue.append(starting_atom)

    while len(panes_in_path) < len(sbu_atoms):
        atom = explore_queue.popleft()
        for neighbor in in_sbu_neighbors(atom, sbu_atoms):
            panes_from_start_to_neighbor: PanesCrossed = panes_in_path[atom] + panes_crossed_in_bond(atom, neighbor)
            if neighbor in panes_in_path:  # ie, if it has already been visted (or at least queued to explore)
                # If the two paths go through different numbers of panes, then it wraps around
                if panes_in_path[neighbor].total() != panes_from_start_to_neighbor.total():
                    return True
            else:
                panes_in_path[neighbor] = panes_from_start_to_neighbor
                explore_queue.append(neighbor)
    return False


def in_sbu_neighbors(atom, sbu_atoms):
    return [neighbor for neighbor in atom.bondedAtoms if neighbor in sbu_atoms]


def panes_crossed_in_bond(a, b):
    atom_1, atom_2 = a, b
    while not atom_1.is_in_unit_cell():
        atom_1 = atom_1.original
    while not atom_2.is_in_unit_cell():
        atom_2 = atom_2.original
    panes_crossed = PanesCrossed()
    if Distances.are_within_bond_range(atom_1, atom_2):
        return panes_crossed  # only works on MOFS with unit cell lengths > 8ish; I hope that's not a problem
    if atom_2.a - atom_1.a > 0.5:
        panes_crossed.a += 1
    elif atom_2.a - atom_1.a < -0.5:
        panes_crossed.a -= 1
    if atom_2.b - atom_1.b > 0.5:
        panes_crossed.b += 1
    elif atom_2.b - atom_1.b < -0.5:
        panes_crossed.b -= 1
    if atom_2.c - atom_1.c > 0.5:
        panes_crossed.c += 1
    elif atom_2.c - atom_1.c < -0.5:
        panes_crossed.c -= 1
    return panes_crossed


class PanesCrossed:
    def __init__(self):
        self.a = 0
        self.b = 0
        self.c = 0

    def __add__(self, other):
        result = PanesCrossed()
        result.a = self.a + other.a
        result.b = self.b + other.b
        result.c = self.c + other.c
        return result

    def __str__(self):
        return f"{self.a}, {self.b}, {self.c}"

    def total(self):
        return abs(self.a) + abs(self.b) + abs(self.c)


class SBUIdentifier:
    def __init__(self, mof, show_duplicates, check_to_modify_bonds):
        self.atoms = mof.atoms
        self.mof = mof
        self.atom_to_SBU = dict()
        self.next_group_id = 1
        self.groups = dict()
        self.allow_two_steps = True
        self.show_duplicates = show_duplicates
        self.check_to_modify_bonds = check_to_modify_bonds

    def been_visited(self, atom):
        return atom.label in self.atom_to_SBU

    def mark_group(self, atom, group_id):
        self.atom_to_SBU[atom.label] = group_id

    def group_id_of(self, atom):
        return self.atom_to_SBU[atom.label]

    def run_algorithm(self):
        connectors = list(())
        auxiliaries = list(())
        # Define clusters
        max_steps_used_to_separate_clusters = 12
        clusters = self.get_clusters(max_steps_used_to_separate_clusters)

        # define connectors and auxiliaries
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
        if self.show_duplicates and self.check_to_modify_bonds:
            self.check_auxiliaries_for_connectors(auxiliaries, connectors)  # This function can change bonds
        else:
            clusters = reduce_duplicates(clusters, lambda x, y: x == y)
            connectors = reduce_duplicates(connectors, lambda x, y: x == y)
            if self.check_to_modify_bonds:
                self.check_auxiliaries_for_connectors(auxiliaries, connectors)  # This function can change bonds
                connectors = reduce_duplicates(connectors, lambda x, y: x == y)
            auxiliaries = reduce_duplicates(auxiliaries, lambda x, y: x == y)
        for sbu in clusters + connectors + auxiliaries:
            sbu.normalize_atoms(self.mof)
            sbu.file_content = XyzWriter.atoms_to_xyz_string(sbu.atoms, '')
        return SBUCollection(clusters, connectors, auxiliaries)

    def get_clusters(self, tightness):
        clusters = list(())
        for atom in self.atoms:
            if MofIdentifier.Molecules.Atom.is_metal(atom.type_symbol) and not self.been_visited(atom):
                sbu = self.identify_cluster(atom)
                if sbu.frequency == float('inf') and self.allow_two_steps:
                    if self.does_split_on_bridges(sbu, clusters, tightness):
                        continue  # Don't need to add cluster to clusters here bc in this case there are multiple
                        # clusters, so I just add them all one by one within the does_split_on_bridges function
                    elif tightness < 5:
                        raise InfiniteBandWithTwoStepFindingException
                    else:
                        # reset this SBUIdentifier
                        self.atom_to_SBU = dict()
                        self.next_group_id = 1
                        self.groups = dict()
                        # recurse
                        return self.get_clusters(tightness - 1)
                else:
                    clusters.append(sbu)
                    self.groups[self.next_group_id] = sbu
                    self.next_group_id += 1
        if len(clusters) == 0:
            raise Exception(f'Exiting algorithm early because no metal atoms found for mof {self.mof.label}')
        temp_clusters = reduce_duplicates(clusters, lambda x, y: x == y)
        if len(clusters) == 1 and not is_infinite_band(clusters[0].atoms):
            pass
        elif any(cluster.frequency == 1 or len(cluster.atoms) > 100 or is_infinite_band(cluster.atoms)
                 for cluster in temp_clusters):
            if tightness < 5:
                if self.allow_two_steps:
                    raise InfiniteBandWithTwoStepFindingException
                else:
                    return clusters
            else:
                self.atom_to_SBU = dict()
                self.next_group_id = 1
                self.groups = dict()
                return self.get_clusters(tightness - 1)
        return clusters

    def identify_cluster(self, metal_atom):
        atoms = set()
        self.identify_cluster_recurse(metal_atom, atoms)
        if is_infinite_band(atoms):
            return changeableSBU(self.next_group_id, UnitType.CLUSTER, atoms, float('inf'))
        else:
            return changeableSBU(self.next_group_id, UnitType.CLUSTER, atoms)

    def identify_cluster_recurse(self, metal_atom, atoms):
        atoms.add(metal_atom)
        self.mark_group(metal_atom, self.next_group_id)
        for neighbor in metal_atom.bondedAtoms:
            if Atom.is_metal(neighbor.type_symbol) and not self.been_visited(neighbor):
                self.identify_cluster_recurse(neighbor, atoms)
        # The following section helps to identify more complex nodes by including metal atoms two steps away
        # It does this only when the intermediate molecule (usually Oxygen) ONLY connects to metals.
        if self.allow_two_steps:
            for neighbor in metal_atom.bondedAtoms:
                self.check_for_including_distant_metals(neighbor, atoms)

    def check_for_including_distant_metals(self, possible_in_node_link, atoms):
        if possible_in_node_link.type_symbol != 'O' or len(possible_in_node_link.bondedAtoms) < 2:
            return
        if not self.been_visited(possible_in_node_link):
            # disqualify if the oxygen touches any non-metal atoms
            for second_neighbor in possible_in_node_link.bondedAtoms:
                if second_neighbor.type_symbol == 'C' or second_neighbor.type_symbol == 'H':
                    if len([atom for atom in possible_in_node_link.bondedAtoms if atom.is_metal()]) < 3:
                        return
                elif not second_neighbor.is_metal():
                    return
            atoms.add(possible_in_node_link)
            self.mark_group(possible_in_node_link, self.next_group_id)
            for second_neighbor in possible_in_node_link.bondedAtoms:
                if second_neighbor not in atoms and second_neighbor.is_metal():
                    self.identify_cluster_recurse(second_neighbor, atoms)

    def does_split_on_bridges(self, big_cluster, clusters, tightness):
        if len(big_cluster.atoms) < 120:
            return False
        smaller_clusters, non_node_atoms = split_on_oxygen_bridges(big_cluster.atoms, tightness)
        if len(smaller_clusters) == 1:
            return False
        for atom in non_node_atoms:
            del self.atom_to_SBU[atom.label]
        for atoms in smaller_clusters:
            for atom in atoms:
                self.atom_to_SBU[atom.label] = self.next_group_id
            if is_infinite_band(atoms):
                cluster = changeableSBU(self.next_group_id, UnitType.CLUSTER, atoms, float('inf'))
            else:
                cluster = changeableSBU(self.next_group_id, UnitType.CLUSTER, atoms)
            self.groups[self.next_group_id] = cluster
            self.next_group_id += 1
            clusters.append(cluster)
        return True

    def identify_ligand(self, nonmetal_atom):
        atoms = set()
        adjacent_cluster_ids = set()
        self.identify_ligand_recurse(nonmetal_atom, atoms, adjacent_cluster_ids)
        self.correct_adjacent_cluster_ids(atoms, adjacent_cluster_ids)
        if len(adjacent_cluster_ids) > 1:
            ligand_type = UnitType.CONNECTOR
        else:
            ligand_type = UnitType.AUXILIARY
        if is_infinite_band(atoms):
            return changeableSBU(self.next_group_id, ligand_type, atoms, float('inf'), adjacent_cluster_ids)
        else:
            return changeableSBU(self.next_group_id, ligand_type, atoms, 1, adjacent_cluster_ids)

    def identify_ligand_recurse(self, nonmetal_atom, ligand_atoms, adjacent_cluster_ids):
        ligand_atoms.add(nonmetal_atom)
        self.mark_group(nonmetal_atom, self.next_group_id)
        for neighbor in nonmetal_atom.bondedAtoms:
            if not self.been_visited(neighbor):
                self.identify_ligand_recurse(neighbor, ligand_atoms, adjacent_cluster_ids)
            elif Atom.is_metal(neighbor.type_symbol):
                adjacent_cluster_ids.add(self.group_id_of(neighbor))

    def successfully_adds_to_cluster(self, atom):
        num_cluster_neighbors = 0
        num_noncluster_neighbors = 0
        noncluster_neighbor = None
        cluster_ids = set()
        cluster = None
        for neighbor in atom.bondedAtoms:
            if self.been_visited(neighbor):
                cluster = self.groups[self.group_id_of(neighbor)]
                if cluster.type == UnitType.CLUSTER:
                    num_cluster_neighbors += 1
                    cluster_ids.add(cluster.sbu_id)
                else:
                    num_noncluster_neighbors += 1  # Because non-node atoms are evaluated one at a time,
                    # it is possible that some linkers have been defined when this line of code executs.
            else:
                num_noncluster_neighbors += 1
                noncluster_neighbor = neighbor

        if atom.type_symbol == 'H':
            if len(atom.bondedAtoms) > 1:
                print(f"Potential error: {atom.label} in {self.mof.label} bonded to multiple atoms")
            for neighbor in atom.bondedAtoms:
                if self.successfully_adds_to_cluster(neighbor):
                    cluster = self.groups[self.group_id_of(neighbor)]
                    cluster.add_atom(atom)
                    self.mark_group(atom, cluster.sbu_id)
                    cluster.add_atom(atom)
                    self.mark_group(atom, cluster.sbu_id)
                    return True

        if len(atom.bondedAtoms) <= 1:
            return False
        elif len(cluster_ids) != 1:
            return False
        if num_noncluster_neighbors == 0 and num_cluster_neighbors > 1:
            cluster.add_atom(atom)
            self.mark_group(atom, cluster.sbu_id)
            return True
        elif num_noncluster_neighbors > 1:
            return False
        elif num_noncluster_neighbors >= num_cluster_neighbors:
            return False
        else:
            if noncluster_neighbor.type_symbol in ['C', 'O', 'H']:
                cluster.add_atom(atom)
                self.mark_group(atom, cluster.sbu_id)
                return True
            else:
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

    def correct_adjacent_cluster_ids(self, ligand_atoms, adjacent_cluster_ids):
        # If it can touch an atom (ie part of a cluster) by going through different panes,
        # then it actually touches that atom twice, in two different copies of the unit cell- so, another connection
        for starting_atom in ligand_atoms:
            self.correct_adjacent_recurse(ligand_atoms, adjacent_cluster_ids, set(), dict(), starting_atom,
                                          PanesCrossed(), dict())
            break

    def correct_adjacent_recurse(self, ligand_atoms, adjacent_cluster_ids, visited, num_panes_to_cluster,
                                 atom, panes_crossed_so_far, representative_atom_of_cluster):
        visited.add(atom)
        for neighbor in atom.bondedAtoms:
            panes_crossed_to_neighbor = panes_crossed_so_far + panes_crossed_in_bond(atom, neighbor)
            if neighbor in ligand_atoms:
                if neighbor not in visited:
                    self.correct_adjacent_recurse(ligand_atoms, adjacent_cluster_ids, visited, num_panes_to_cluster,
                                                  neighbor, panes_crossed_to_neighbor, representative_atom_of_cluster)
            else:  # must belong to a cluster, by definition of ligand
                cluster_id = self.atom_to_SBU[neighbor.label]
                if cluster_id in representative_atom_of_cluster:
                    repr_atom = representative_atom_of_cluster[cluster_id]
                    # The panes between the starting atom and the atom chosen to represent this cluster (through this
                    # path) is equal to [the panes between the neighbor and its cluster's representative,
                    # traveling within the cluster] plus [the panes crossed from the starting atom to the neighbor]
                    panes_to_repr_atom = panes_between(neighbor, repr_atom, self.groups[cluster_id]) \
                                         + panes_crossed_to_neighbor
                    if panes_to_repr_atom.total() != num_panes_to_cluster[repr_atom.label].total():
                        adjacent_cluster_ids.add(-1 * cluster_id)  # Negative to signify that the two connections reach
                        # different copies of the same cluster
                else:
                    representative_atom_of_cluster[cluster_id] = neighbor
                    num_panes_to_cluster[neighbor.label] = panes_crossed_to_neighbor

    @classmethod
    def copy_from(cls, other):
        return SBUIdentifier(other.mof, other.show_duplicates, other.check_to_modify_bonds)

    def check_auxiliaries_for_connectors(self, auxiliaries, connectors):
        aux_to_become_conn = list()
        for aux in auxiliaries:
            for conn in connectors:
                if self.make_bonds_to_match_conn(aux, conn):  # This function can change bonds
                    aux_to_become_conn.append(aux)
                    break
        for sbu in aux_to_become_conn:
            auxiliaries.remove(sbu)
            connectors.append(sbu)

    def make_bonds_to_match_conn(self, aux, conn):
        is_match, aux_label_to_conn_label, = SubGraphMatcher.mapping_function(aux, conn)

        def aux_to_conn(atom):
            match_label = aux_label_to_conn_label(atom.label)
            return next(a for a in conn.atoms if a.label == match_label)

        if not is_match:
            return False

        has_added_bonds = False
        for atom in aux.atoms:
            try:
                match = aux_to_conn(atom)
                if len(match.bondedAtoms) > len(atom.bondedAtoms):
                    excess_freq_of_element = collections.defaultdict(lambda: 0)
                    for a in match.bondedAtoms:
                        excess_freq_of_element[a.type_symbol] += 1
                    for a in atom.bondedAtoms:
                        excess_freq_of_element[a.type_symbol] -= 1
                    for elem in (elem for elem, freq in excess_freq_of_element.items() if freq > 0):
                        has_added_bonds = has_added_bonds or try_to_bond(atom, elem, self.mof)
            except StopIteration:
                pass
        return has_added_bonds


def try_to_bond(atom, elem, mof):
    candidates = ((a, Distances.distance_across_unit_cells(atom, a, mof.angles, mof.fractional_lengths, mof.unit_volume))
                  for a in mof.atoms if a.type_symbol == elem and a not in atom.bondedAtoms)
    (candidate, dist) = min(candidates, key=lambda x: x[1])
    if dist < Distances.bond_distance(atom, candidate, Distances.bond_length_multiplicative_error_margin + 0.07):
        candidate.bondedAtoms.append(atom)
        atom.bondedAtoms.append(candidate)
        return True
    else:
        return False


def panes_between(start, end, cluster):
    _, panes = panes_between_recurse(start, end, set(), PanesCrossed(), cluster)
    return panes


def panes_between_recurse(atom, end, visited, panes_so_far, cluster):
    if atom == end:
        return True, panes_so_far
    visited.add(atom)
    for neighbor in atom.bondedAtoms:
        if neighbor in cluster.atoms:  # Only look within the cluster
            if neighbor not in visited:
                crosses_pane = panes_crossed_in_bond(atom, neighbor)
                found_end, panes = panes_between_recurse(neighbor, end, visited, panes_so_far + crosses_pane, cluster)
                if found_end:
                    return found_end, panes
    return False, None


def split_on_oxygen_bridges(sbu_atoms, tightness):
    split_points = list()
    for atom in sbu_atoms:
        if atom.type_symbol == 'O':
            neighbors = in_sbu_neighbors(atom, sbu_atoms)
            if len(neighbors) == 2 and all(neighbor.is_metal for neighbor in neighbors):
                # How will we differentiate between oxygens that bridge clusters and oxygens within a cluster?
                # If the two metals it touches have an alternate route between them THAT IS SHORTISH, then it is
                # within a cluster; otherwise, it divides the two metals pretty well into different clusters.
                # The definition of shortish gets tighter until the solution looks right. Extra tightness if the two
                # metals are different.
                penalty = 0 if neighbors[0].type_symbol == neighbors[1].type_symbol else 1
                if penalty:
                    penalty *= abs(CovalentRadiusLookup.lookup(neighbors[0].type_symbol) - CovalentRadiusLookup.lookup(
                        neighbors[1].type_symbol)) / 40
                if not exists_route_with_constraints(neighbors[0], neighbors[1], forbidden_atoms=[atom],
                                                     max_steps=tightness - penalty, max_successive_nonmetal_steps=3):
                    split_points.append(atom)
    visited = list()
    explore_queue = collections.deque()
    clusters = list()
    for starting_atom in sbu_atoms:
        if starting_atom not in visited and starting_atom not in split_points:
            visited.append(starting_atom)
            cluster = set()
            cluster.add(starting_atom)
            explore_queue.append(starting_atom)
            while len(explore_queue) > 0:
                atom = explore_queue.popleft()
                for neighbor in (n for n in atom.bondedAtoms if n in sbu_atoms and n not in split_points):
                    if neighbor not in visited:
                        visited.append(neighbor)
                        cluster.add(neighbor)
                        explore_queue.append(neighbor)
            clusters.append(cluster)
    # If at least one larger cluster and not too many weirdly sized clusters
    if any(len(cluster) > 10 for cluster in clusters) \
            and len([cluster for cluster in clusters if 2 <= len(cluster) <= 5]) < 12:
        return clusters, split_points
    else:
        return [sbu_atoms], split_points


def exists_route_with_constraints(start, end, forbidden_atoms, max_steps,
                                  max_successive_nonmetal_steps):
    # This could be phrased as a recursive algorithm, but it is slower that way.
    branches = deque()
    # Start, forbidden atoms, steps_left, successive_nonmetal_steps)
    branches.append((start, forbidden_atoms, max_steps, 0))
    while len(branches) > 0:
        (atom, f, steps_left, successive_nonmetal_steps) = branches.popleft()
        if steps_left < 1:
            continue
        if successive_nonmetal_steps == max_successive_nonmetal_steps:
            continue
        for neighbor in atom.bondedAtoms:
            if neighbor == end:
                return True
            if neighbor in f:
                continue
            branches.append((neighbor, f + [atom], steps_left - 1,
                             0 if neighbor.is_metal() else successive_nonmetal_steps + 1))
    return False
