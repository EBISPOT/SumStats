import sqlite3


class sqlClient():
    def __init__(self, database):
        self.database = database
        self.conn = self.create_conn()
        self.cur = self.conn.cursor()

    def create_conn(self):
        try:
            conn = sqlite3.connect(self.database)
            return conn
        except NameError as e:
            print(e)
        return None


    """ INSERT STATEMENTS """

    def insert_snp_row(self, data):
        self.cur.execute("insert or ignore into snp values (?,?,?)", data)

    def insert_trait_row(self, data):
        self.cur.execute("insert or ignore into trait values (?)", (data,))

    def insert_study_row(self, data):
        self.cur.execute("insert or ignore into study (study) values (?)", (data,))

    def insert_tissue_row(self, data):
        self.cur.execute("insert or ignore into tissue values (?)", (data,))

    def insert_uuid_row(self, data):
        self.cur.execute("insert or ignore into uuid values (?,?,?,?)", data)



    """ SELECT STATEMENTS """


    def get_chr_pos(self, snp):
        data = []
        for row in self.cur.execute("SELECT chr, position FROM snp WHERE rsid=?", (snp,)):
            data.append(row)
        if data:
            return data
        else:
            return False

    def get_uuid_from_study(self, study):
        uuids = []
        for row in self.cur.execute("select * from uuid join study on uuid.study_id = study.rowid where study.study =?", (study,)):
            uuids.append(row[0])
        if uuids:
            return uuids
        else:
            return False

    def get_uuid_from_trait(self, trait):
        uuids = []
        for row in self.cur.execute("select * from uuid join trait on uuid.trait_id = trait.rowid where trait.trait =?", (trait,)):
            uuids.append(row[0])
        if uuids:
            return uuids
        else:
            return False

    def get_studies(self):
        data = []
        for row in self.cur.execute("SELECT study FROM study_info"):
            data.append(row[0])
        if data:
            return data
        else:
            return False

    def get_study_context_meta(self, identifier):
        data_dict = {"study": None, 
                     "identifier": None,
                     "qtl_group": None,
                     "tissue_label": None,
                     "phen": None,
                     "tissue_ont": None,
                     "condition": None,
                     "quant_method": None,
                     "condition_label": None
                     }

        #self.cur.execute("SELECT * FROM study_info where identifier =?", (identifier,))

        self.cur.execute("""
                          SELECT s.study, s.identifier, q.qtl_group, q.cell_type, s.trait_file, q.ontology_term, q.condition, q.condition_label 
                          FROM qtl_context_mapping AS q 
                          JOIN study_info AS s 
                          ON q.study = s.study AND q.qtl_group = s.qtl_group 
                          WHERE s.identifier =?
                          """, (identifier,))

        data = self.cur.fetchone()
        if data:
            data_dict["study"], data_dict["identifier"], data_dict["qtl_group"], data_dict["tissue_label"], data_dict["phen"], data_dict["tissue_ont"], data_dict["condition"], data_dict["condition_label"] = data
        return data_dict

    def get_traits(self):
        data = []
        for row in self.cur.execute("SELECT trait FROM study_info"):
            data.append(row[0])
        if data:
            return data
        else:
            return False

    def get_tissues(self):
        data = []
        for row in self.cur.execute("SELECT tissue FROM study_info"):
            data.append(row[0])
        if data:
            return data
        else:
            return False

    def get_tissue_ontos(self):
        data = []
        for row in self.cur.execute("SELECT tissue_ontology FROM study_info"):
            data.append(row[0])
        if data:
            return data
        else:
            return False

    def get_studies_for_trait(self, trait):
        data = []
        for row in self.cur.execute("select study from study_info where trait =?", (trait,)):
            data.append(row[0])
        if data:
            return data
        else:
            return False

    def get_traits_for_study(self, study):
        data = []
        for row in self.cur.execute("select trait from study_info where study =?", (study,)):
            data.append(row[0])
        if data:
            return data
        else:
            return False

    def get_file_id_for_study(self, study, quant):
        data = []
        for row in self.cur.execute("select identifier from study_info where study =? and quant_method =?", (study, quant)):
            data.append(row[0])
        if data:
            return data
        else:
            return False

    def get_file_ids_for_study_tissue(self, study, tissue, quant):
        data = []
        for row in self.cur.execute("select identifier from study_info where study =? and tissue_ontology =? and quant_method =?", (study, tissue, quant)):
            data.append(row[0])
        if data:
            return data
        else:
            return False

    def get_file_ids_for_qtl_group(self, qtl_group, quant):
        data = []
        for row in self.cur.execute("select identifier from study_info where qtl_group =? and quant_method =?", (qtl_group, quant)):
            data.append(row[0])
        if data:
            return data
        else:
            return False

    def get_file_ids_for_study_qtl_group(self, study, qtl_group, quant):
        data = []
        for row in self.cur.execute("select identifier from study_info where study =? and qtl_group =? and quant_method =?", (study, qtl_group, quant)):
            data.append(row[0])
        if data:
            return data
        else:
            return False

    def get_file_id_for_trait(self, trait):
        data = []
        for row in self.cur.execute("select file_id from study join study_info on study.study = study_info.study where trait =?", (trait,)):
            data.append(row[0])
        if data:
            return data
        else:
            return False

    def get_file_ids_for_tissue(self, tissue, quant):
        data = []
        for row in self.cur.execute("select identifier from study_info where tissue_ontology =? and quant_method =?", (tissue, quant)):
            data.append(row[0])
        if data:
            return data
        else:
            return False

    def get_chrom_for_trait(self, trait):
        self.cur.execute("SELECT chromosome FROM study_info where phenotype_id =?", (trait,))
        data = self.cur.fetchone()
        if data is not None:
            return data[0]
        else:
            return False

    def get_study_rowid(self, study):
        self.cur.execute("SELECT rowid FROM study where study =?", (study,))
        data = self.cur.fetchone()
        if data is not None:
            return data[0]
        else:
            return False

    def get_trait_rowid(self, trait):
        self.cur.execute("SELECT rowid FROM trait where trait =?", (trait,))
        data = self.cur.fetchone()
        if data is not None:
            return data[0]
        else:
            return False

    def get_tissue_rowid(self, tissue):
        self.cur.execute("SELECT rowid FROM tissue where tissue =?", (tissue,))
        data = self.cur.fetchone()
        if data is not None:
            return data[0]
        else:
            return False

    def get_studies_for_tissue(self, tissue):
        data = []
        for row in self.cur.execute("select study from study_info where tissue_ontology =?", (tissue,)):
            data.append(row[0])
        if data:
            return data
        else:
            return False

    def check_study(self, study):
        data = []
        for row in self.cur.execute("SELECT study FROM study_info where study =?", (study,)):
            data.append(row[0])
        if data:
            return True
        else:
            return False


    """ OTHER STATEMENTS """

    def commit(self):
        self.cur.execute("COMMIT")

    def drop_rsid_index(self):
        self.cur.execute("DROP INDEX rsid_idx")

    def create_rsid_index(self):
        self.cur.execute("CREATE INDEX rsid_idx on snp (rsid)")
