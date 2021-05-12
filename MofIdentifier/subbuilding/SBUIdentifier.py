import MofIdentifier
from MofIdentifier.CifReader import read_mof
from MofIdentifier.MofBondCreator import MofBondCreator
from MofIdentifier.subbuilding.SBUs import SBUs, SBU, UnitType


def split(mof):
    identifier = SBUIdentifier(mof)
    return identifier.run_algorithm()


def reduce_duplicates(sbu_list):
    sbu_list = sbu_list.copy()
    new_sbu_list = list()
    i = 0
    while i < len(sbu_list):
        new_sbu_list.append(sbu_list[i])
        j = i + 1
        while j < len(sbu_list):
            if sbu_list[i] == (sbu_list[j]):
                new_sbu_list[i].frequency += 1
                sbu_list.pop(j)
            else:
                j += 1
        i += 1
    return new_sbu_list


class SBUIdentifier:
    def __init__(self, mof):
        self.atoms = mof.atoms
        self.atom_to_SBU = dict()
        self.num_groups = 0
        self.groups = list(())

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
            if MofIdentifier.atom.isMetal(atom.type_symbol) and not self.been_visited(atom):
                sbu = self.identify_cluster(atom)
                clusters.append(sbu)
                self.groups.append(sbu)
                self.num_groups += 1
        if len(clusters) == 0:
            raise Exception('Exiting algorithm early because no metal atoms found')
        for atom in self.atoms:
            if not self.been_visited(atom):
                if self.successfully_adds_to_cluster(atom):
                    continue
                sbu = self.identify_ligand(atom)
                self.groups.append(sbu)
                if sbu.type == UnitType.CONNECTOR:
                    connectors.append(sbu)
                else:
                    auxiliaries.append(sbu)
                self.num_groups += 1
        for cluster in clusters:
            self.set_adj_ids(cluster)
        if len(connectors) == 0:
            raise Exception('Exiting algorithm early because no connectors found')
        clusters = reduce_duplicates(clusters)
        connectors = reduce_duplicates(connectors)
        auxiliaries = reduce_duplicates(auxiliaries)
        return SBUs(clusters, connectors, auxiliaries)

    def identify_cluster(self, metal_atom):
        cluster = set(())
        self.identify_cluster_recurse(metal_atom, cluster)
        return SBU(self.num_groups, UnitType.CLUSTER, cluster)

    def identify_cluster_recurse(self, metal_atom, cluster):
        cluster.add(metal_atom)
        self.mark_group(metal_atom, self.num_groups)
        for neighbor in metal_atom.bondedAtoms:
            if MofIdentifier.atom.isMetal(neighbor.type_symbol) and not self.been_visited(neighbor):
                self.identify_cluster_recurse(neighbor, cluster)
        for neighbor in metal_atom.bondedAtoms:
            if not self.been_visited(neighbor):
                has_been_added = False
                for second_neighbor in neighbor.bondedAtoms:
                    if MofIdentifier.atom.isMetal(second_neighbor.type_symbol) and not self.been_visited(
                            second_neighbor):
                        if not has_been_added:
                            cluster.add(neighbor)
                            self.mark_group(neighbor, self.num_groups)
                            has_been_added = True
                        self.identify_cluster_recurse(second_neighbor, cluster)

    def identify_ligand(self, nonmetal_atom):
        ligand = SBU(self.num_groups, None, set(()))
        self.identify_ligand_recurse(nonmetal_atom, ligand)
        if len(ligand.adjacent_cluster_ids) > 1:
            ligand.type = UnitType.CONNECTOR
        else:
            ligand.type = UnitType.AUXILIARY
        return ligand

    def identify_ligand_recurse(self, nonmetal_atom, ligand):
        ligand.atoms.add(nonmetal_atom)
        self.mark_group(nonmetal_atom, self.num_groups)
        for neighbor in nonmetal_atom.bondedAtoms:
            if not self.been_visited(neighbor):
                self.identify_ligand_recurse(neighbor, ligand)
            elif MofIdentifier.atom.isMetal(neighbor.type_symbol):
                ligand.adjacent_cluster_ids.add(
                    self.group_id_of(neighbor))

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
                    num_noncluster_neighbors += 1
            else:
                num_noncluster_neighbors += 1
        if atom.type_symbol == 'H':
            for neighbor in atom.bondedAtoms:
                if self.successfully_adds_to_cluster(neighbor):
                    cluster = self.groups[self.group_id_of(neighbor)]
                    cluster.atoms.add(atom)
                    self.mark_group(atom, cluster.sbu_id)
                    return True
        if num_cluster_neighbors > num_noncluster_neighbors and len(cluster_ids) == 1:
            # if num_noncluster_neighbors == 1 then it's likely to be part of an aux sbu, not part of the cluster
            cluster.atoms.add(atom)
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


if __name__ == '__main__':
    mof = read_mof('../smod7-pos-1.cif')
    bond_creator = MofBondCreator(mof)
    bond_creator.connect_atoms()
    print(mof)
    split_mof = split(mof)
    print(split_mof)
