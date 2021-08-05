from GUI.Views import LigandView, SBUView, MOFView
from MofIdentifier.DAO import LigandDatabase, SBUDatabase, MOFDatabase
from MofIdentifier.Molecules import Ligand, SBU, MOF


def make_view(parent, molecule):
    if isinstance(molecule, LigandDatabase.LigandDatabase) or isinstance(molecule, Ligand.Ligand):
        return LigandView.View(parent, molecule)
    elif isinstance(molecule, SBUDatabase.SBUDatabase) or isinstance(molecule, SBU.SBU):
        return SBUView.View(parent, molecule)
    elif isinstance(molecule, MOFDatabase.MOFDatabase) or isinstance(molecule, MOF.MOF):
        return MOFView.View(parent, molecule)
    else:
        raise Exception(f"MoleculeView requires a ligand or SBU to construct, not a {type(molecule)}")
