from MofIdentifier.Molecules import Molecule


class Ligand(Molecule.Molecule):
    def __init__(self, label, atoms):
        super().__init__(label, atoms)
        for atom in atoms:
            self.elementsPresent.add(atom.type_symbol)

    def __str__(self):
        return "{} ligand".format(self.label)
