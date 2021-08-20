from MofIdentifier.fileIO import LigandReader


class LigandDatabase:
    def __init__(self, ligand_name, ligand_file, Mofs):
        self.name = ligand_name
        self.file_content = ligand_file
        self.Mofs = Mofs
        self._ligand = None

    def set_ligand_name(self, name):
        self.ligand_name = name

    def set_ligand_file(self, file):
        self.ligand_file = file

    def set_Mofs(self, mofs):
        self.Mofs = mofs

    def get_ligand(self):
        if self._ligand is None:
            if self.file_content is not None:
                if len(self.file_content.split('\n')) > 2:
                    name = self.name + '.xyz'
                else:
                    name = self.name + '.smiles'
                self._sbu = LigandReader.get_mol_from_string(self.file_content, name)
            else:
                return None
        return self._sbu

    @classmethod
    def from_dict(cls, ligand_obj):
        return cls(ligand_obj["ligand_name"], ligand_obj["ligand_file_content"], ligand_obj["MOFs"])
