import pandas as pd


class metaClient():
    def __init__(self, metafile):
        self.metafile = metafile


    def get_chr_pos(self, snp):
        data = []
        search_string = "rsid == {snp}".format(snp)
        with pd.HDFStore(self.metafile) as store:
            results = store.select('snp', where=search_string)
            data.append((results['chr'].values[0], results['position'].values[0]))
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
        for row in self.cur.execute("SELECT study FROM study_trait"):
            data.append(row[0])
        if data:
            return data
        else:
            return False

    def get_traits(self):
        data = []
        for row in self.cur.execute("SELECT trait FROM study_trait"):
            data.append(row[0])
        if data:
            return data
        else:
            return False

    def get_studies_for_trait(self, trait):
        data = []
        for row in self.cur.execute("select study from study_trait where trait =?", (trait,)):
            data.append(row[0])
        return data

    def get_traits_for_study(self, study):
        data = []
        for row in self.cur.execute("select trait from study_trait where study =?", (study,)):
            data.append(row[0])
        return data


    def get_file_id_for_study(self, study):
        data = []
        for row in self.cur.execute("select file_id from study where study =?", (study,)):
            data.append(row[0])
        return data

    def get_file_id_for_trait(self, trait):
        data = []
        for row in self.cur.execute("select file_id from study join study_trait on study.study = study_trait.study where trait =?", (trait,)):
            data.append(row[0])
        return data
