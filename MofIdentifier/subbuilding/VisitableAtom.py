class VisitableAtom:
    def __init__(self, atom):
        self.label = atom.label
        self.type_symbol = atom.type_symbol
        self.bondedAtoms = list(())
        self.hasBeenVisited = False

    def __str__(self):
        bonds_string = ''
        for atom in self.bondedAtoms:
            bonds_string = bonds_string + atom.label + ', '
        return "{name} visited={visit} at bonded to {bonds}".format(name=self.label, visit=self.hasBeenVisited, bonds=bonds_string)

    def __eq__(self, other):
        return self.label == other.label

    def __hash__(self):
        return hash(self.label)


def convert(atoms):
    new_atoms = list()
    for atom in atoms:
        new_atoms.append(VisitableAtom(atom))
    for i in range(len(atoms)):

    return new_atoms