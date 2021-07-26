from GUI.Views import LigandView, SBUView
from MofIdentifier.Molecules import Ligand, SBU


def make_view(parent, molecule):
    if isinstance(molecule, Ligand.Ligand):
        return LigandView.View(parent, molecule)
    elif isinstance(molecule, SBU.SBU):
        return SBUView.View(parent, molecule)
    else:
        raise Exception("MoleculeView requires a ligand or SBU to construct.")
