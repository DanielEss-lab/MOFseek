from GUI import LigandView, SBUView
from MofIdentifier.Molecules import Ligand
from MofIdentifier.subbuilding import SBUTools


def make_view(parent, molecule):
    if isinstance(molecule, Ligand.Ligand):
        return LigandView.make_view(parent, molecule)
    elif isinstance(molecule, SBUTools.SBU):
        return SBUView.make_view(parent, molecule)
    else:
        raise Exception("MoleculeView requires a ligand or SBU to construct.")
