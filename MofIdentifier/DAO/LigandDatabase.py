class LigandDatabase:
    def __init__(self, ligand_name, ligand_file, Mofs):
        self.ligand_name = ligand_name
        self.ligand_file = ligand_file
        self.Mofs = Mofs

    def set_ligand_name(self, name):
        self.ligand_name = name

    def set_ligand_file(self, file):
        self.ligand_file = file

    def set_Mofs(self, mofs):
        self.Mofs = mofs
