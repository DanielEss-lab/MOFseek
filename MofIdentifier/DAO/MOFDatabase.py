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
        set_from_dictionary_or_mof('atoms_string_without_solvents')

        self.ligand_names = get_or_calculate('ligand_names', lambda mof: LigandDAO.scan_all_for_mof(mof))
        if self.get_mof() is not None:
            sbu_node_info = get_or_calculate('sbu_node_info', lambda mof: SBUDAO.process_sbus(mof.sbus().clusters, mof))
            self.sbu_nodes = [ContainedSBU(info) for info in sbu_node_info]
            sbu_conn_info = get_or_calculate('sbu_connector_info', lambda mof: SBUDAO.process_sbus(mof.sbus().connectors, mof))
            self.sbu_connectors = [ContainedSBU(info) for info in sbu_conn_info]
            sbu_aux_info = get_or_calculate('sbu_aux_info', lambda mof: SBUDAO.process_sbus(mof.sbus().auxiliaries, mof))
            self.sbu_auxiliaries = [ContainedSBU(info) for info in sbu_aux_info]
        else:
            self.sbu_nodes = self.sbu_connectors = self.sbu_auxiliaries = None

        self.LCD = dictionary['LCD']
        self.PLD = dictionary['PLD']
        self.LFPD = dictionary['LFPD']
        self.cm3_g = dictionary['cm3_g']
        self.ASA_m2_cm3 = dictionary['ASA_m2_cm3']
        self.ASA_m2_g = dictionary['ASA_m2_g']
        self.NASA_m2_cm3 = dictionary['NASA_m2_cm3']
        self.NASA_m2_g = dictionary['NASA_m2_g']
        self.AV_VF = dictionary['AV_VF']
        self.AV_cm3_g = dictionary['AV_cm3_g']
        self.NAV_cm3_g = dictionary['NAV_cm3_g']
        self.All_Metals = dictionary['All_Metals']
        self.Has_OMS = dictionary['Has_OMS']
        self.Open_Metal_Sites = dictionary['Open_Metal_Sites']
        self.Extension = dictionary['Extension']
        self.FSR_overlap = dictionary['FSR_overlap']
        self.from_CSD = dictionary['from_CSD']
        self.public = dictionary['public']
        self.DISORDER = dictionary['DISORDER']
        self.CSD_overlap_inCoRE = dictionary['CSD_overlap_inCoRE']
        self.CSD_of_WoS_inCoRE = dictionary['CSD_of_WoS_inCoRE']
        self.CSD_overlap_inCCDC = dictionary['CSD_overlap_inCCDC']
        self.date_CSD = dictionary['date_CSD']
        self.DOI_public = dictionary['DOI_public']
        self.Note = dictionary['Note']
        self.Matched_CSD_of_CoRE = dictionary['Matched_CSD_of_CoRE']
        self.Possible_List_CSD_of_CoRE = dictionary['Possible_List_CSD_of_CoRE']

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
