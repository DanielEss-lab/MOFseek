from GUI.Views import LigandView, SBUView
from MofIdentifier.DAO import LigandDatabase, SBUDatabase
from MofIdentifier.Molecules import Ligand, SBU


def make_view(parent, molecule):
    if isinstance(molecule, LigandDatabase.LigandDatabase) or isinstance(molecule, Ligand.Ligand):
        return LigandView.View(parent, molecule)
    elif isinstance(molecule, SBUDatabase.SBUDatabase) or isinstance(molecule, SBU.SBU):
        return SBUView.View(parent, molecule)
    else:
        raise Exception(f"MoleculeView requires a ligand or SBU to construct, not a {type(molecule)}")
