from MofIdentifier.Molecules import Molecule


class Ligand(Molecule.Molecule):
    def __init__(self, filepath, atoms, file_string):
        self.file_content = file_string
        super().__init__(filepath, atoms)

    def __str__(self):
        return "{} ligand".format(self.label)
