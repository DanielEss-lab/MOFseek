from GUI.Views import LigandView, SBUView, MOFView
from DAO import LigandDatabase, SBUDatabase, MOFDatabase


def make_view(parent, molecule):
    if isinstance(molecule, LigandDatabase.LigandDatabase):
        return LigandView.View(parent, molecule)
    elif isinstance(molecule, SBUDatabase.SBUDatabase):
        return SBUView.View(parent, molecule)
    elif isinstance(molecule, MOFDatabase.MOFDatabase):
        return MOFView.View(parent, molecule)
    else:
        raise Exception(f"MoleculeView requires a ligand or SBU to construct, not a {type(molecule)}")
