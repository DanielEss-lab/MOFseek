from GUI import LigandView, SBUView
from MofIdentifier.Molecules import Ligand, SBU


def make_view(parent, molecule):
    if isinstance(molecule, Ligand.Ligand):
        return LigandView.make_view(parent, molecule)
    elif isinstance(molecule, SBU.SBU):
        return SBUView.make_view(parent, molecule)
    else:
        raise Exception("MoleculeView requires a ligand or SBU to construct.")
