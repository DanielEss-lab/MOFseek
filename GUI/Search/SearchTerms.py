from pathlib import Path

from MofIdentifier.SubGraphMatching import SubGraphMatcher
from MofIdentifier.fileIO import CifReader
from MofIdentifier.subbuilding import SBUIdentifier


class SearchTerms:
    def __init__(self, ligands=None, element_symbol_list=None, excl_ligands=None, excl_elements=None, sbus=None,
                 excl_sbus=None):
        if excl_sbus is None:
            excl_sbus = []
        if sbus is None:
            sbus = []
        if excl_elements is None:
            excl_elements = []
        if excl_ligands is None:
            excl_ligands = []
        if ligands is None:
            ligands = []
        if element_symbol_list is None:
            element_symbol_list = []
        self.ligands = ligands
        self.element_symbols = element_symbol_list
        self.excl_ligands = excl_ligands
        self.excl_element_symbols = excl_elements
        self.sbus = sbus
        self.excl_sbus = excl_sbus
        # Add parameters here

    def passes(self, MOF):
        for element in self.element_symbols:
            if element not in MOF.elementsPresent:
                return False
        for element in self.excl_element_symbols:
            if element in MOF.elementsPresent:
                return False
        if SBUIdentifier.mof_has_all_sbus(MOF, self.sbus) and SBUIdentifier.mof_has_no_sbus(MOF, self.excl_sbus):
            pass
        else:
            return False
        if SubGraphMatcher.mof_has_all_ligands(MOF, self.ligands) \
                and SubGraphMatcher.mof_has_no_ligands(MOF, self.excl_ligands):
            pass
        else:
            return False
        return True

    def __str__(self):
        ligands = [ligand.label for ligand in self.ligands]
        excl_ligands = [ligand.label for ligand in self.excl_ligands]
        sbus = [sbu.label for sbu in self.sbus]
        excl_sbus = [sbu.label for sbu in self.excl_sbus]
        return f"ligands:{ligands}-{excl_ligands}, " + \
               f"elements:{self.element_symbols}-{self.excl_element_symbols}" + \
               f"sbus:{sbus}-{excl_sbus}"

    def __eq__(self, other):
        return str(self) == str(other)

    def __hash__(self):
        return hash(str(self))


def search_ligand_names_in_mofsForTests(search):
    path = str(Path(__file__).parent / "../../MofIdentifier/mofsForTests")
    mofs = CifReader.get_all_mofs_in_directory(path)
    good_mofs = [mof for mof in mofs if search.passes(mof)]
    return good_mofs