from MofIdentifier.Molecules import Molecule


class Ligand(Molecule.Molecule):
    def __init__(self, filepath, atoms):
        super().__init__(filepath, atoms)
        for atom in atoms:
            self.elementsPresent.add(atom.type_symbol)

    def __str__(self):
        return "{} ligand".format(self.label)
