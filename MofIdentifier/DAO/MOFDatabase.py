from MofIdentifier.DAO import SBUDAO, LigandDAO
from MofIdentifier.fileIO import CifReader


class ContainedSBU:
    def __init__(self, info_string):
        self.frequency, self.connectivity, self.name = info_string.split(' ', 2)


class MOFDatabase:
    def __init__(self, dictionary):
        self.filename = dictionary['filename']
        try:
            self.file_content = dictionary['cif_content']
        except KeyError:
            self.file_content = None
        self._mof = None

        def set_from_dictionary_or_mof(attribute_name):
            try:
                setattr(self, attribute_name, dictionary[attribute_name])
            except KeyError:
                if self.get_mof() is not None:
                    # use cif content to make MOF object, get attribute from that
                    setattr(self, attribute_name, getattr(self.get_mof(), attribute_name))
                else:
                    setattr(self, attribute_name, None)

        def get_or_calculate(attribute_name, calculator):
            try:
                return dictionary[attribute_name]
            except KeyError:
                if self.get_mof() is not None:
                    # use cif content to make MOF object, calculate attribute from that
                    return calculator(self.get_mof())
                else:
                    return None

        set_from_dictionary_or_mof('symmetry')
        set_from_dictionary_or_mof('fractional_lengths')
        set_from_dictionary_or_mof('angles')
        set_from_dictionary_or_mof('unit_volume')
        set_from_dictionary_or_mof('cartesian_lengths')
        set_from_dictionary_or_mof('elementsPresent')
        set_from_dictionary_or_mof('atoms_string_with_solvents')
        self.atoms_string_with_solvents = get_or_calculate('atoms_string_with_solvents',
                                                           lambda mof: mof.atoms_string_with_solvents())
        self.atoms_string_without_solvents = get_or_calculate('atoms_string_without_solvents',
                                                           lambda mof: mof.atoms_string_without_solvents())

        self.ligand_names = get_or_calculate('ligand_names', lambda mof: LigandDAO.scan_all_for_mof(mof))
        if self.get_mof() is not None:
            sbu_node_info = dictionary['sbu_node_info']
            self.sbu_nodes = [ContainedSBU(info) for info in sbu_node_info]
            sbu_conn_info = dictionary['sbu_conn_info']
            self.sbu_connectors = [ContainedSBU(info) for info in sbu_conn_info]
            sbu_aux_info = dictionary['sbu_aux_info']
            self.sbu_auxiliaries = [ContainedSBU(info) for info in sbu_aux_info]
            self.sbu_names = [SBU.name for SBU in self.sbu_nodes]
            self.sbu_names.extend([SBU.name for SBU in self.sbu_connectors])
            self.sbu_names.extend([SBU.name for SBU in self.sbu_auxiliaries])
        else:
            self.sbu_nodes = self.sbu_connectors = self.sbu_auxiliaries = None
            self.sbu_names = []

        self.LCD = dictionary.get('LCD')
        self.PLD = dictionary.get('PLD')
        self.LFPD = dictionary.get('LFPD')
        self.cm3_g = dictionary.get('cm3_g')
        self.ASA_m2_cm3 = dictionary.get('ASA_m2_cm3')
        self.ASA_m2_g = dictionary.get('ASA_m2_g')
        self.NASA_m2_cm3 = dictionary.get('NASA_m2_cm3')
        self.NASA_m2_g = dictionary.get('NASA_m2_g')
        self.AV_VF = dictionary.get('AV_VF')
        self.AV_cm3_g = dictionary.get('AV_cm3_g')
        self.NAV_cm3_g = dictionary.get('NAV_cm3_g')
        self.All_Metals = dictionary.get('All_Metals')
        self.Has_OMS = dictionary.get('Has_OMS')
        self.Open_Metal_Sites = dictionary.get('Open_Metal_Sites')
        self.Extension = dictionary.get('Extension')
        self.FSR_overlap = dictionary.get('FSR_overlap')
        self.from_CSD = dictionary.get('from_CSD')
        self.public = dictionary.get('public')
        self.DISORDER = dictionary.get('DISORDER')
        self.CSD_overlap_inCoRE = dictionary.get('CSD_overlap_inCoRE')
        self.CSD_of_WoS_inCoRE = dictionary.get('CSD_of_WoS_inCoRE')
        self.CSD_overlap_inCCDC = dictionary.get('CSD_overlap_inCCDC')
        self.date_CSD = dictionary.get('date_CSD')
        self.DOI_public = dictionary.get('DOI_public')
        self.Note = dictionary.get('Note')
        self.Matched_CSD_of_CoRE = dictionary.get('Matched_CSD_of_CoRE')
        self.Possible_List_CSD_of_CoRE = dictionary.get('Possible_List_CSD_of_CoRE')

        self.num_atoms = get_or_calculate('num_atoms', lambda mof: len(mof.atoms))
        self.conn_node_atom_ratio = get_or_calculate('conn_node_atom_ratio', lambda mof:
                mof.sbus().num_connector_atoms / mof.sbus().num_cluster_atoms)
        self.aux_density = get_or_calculate('aux_density', lambda mof: len(mof.sbus().auxiliaries) / mof.unit_volume)
        self.conn_connectivity = get_or_calculate('conn_connectivity', lambda mof: mof.sbus().avg_conn_connectivity)
        self.node_connectivity = get_or_calculate('node_connectivity', lambda mof: mof.sbus().avg_node_connectivity)
        self.elements_present = get_or_calculate('elements_present', lambda mof: mof.elementsPresent)

    def get_mof(self):
        if self._mof is None:
            if self.file_content is not None:
                self._mof = CifReader.read_string(self.file_content, self.filename)
            else:
                return None
        return self._mof
