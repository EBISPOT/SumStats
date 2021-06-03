import pandas as pd
import tables as tb


class metaClient():
    def __init__(self, metafile):
        self.metafile = metafile


    """ LOAD STATEMENTS """

    def load_study_trait(self, study, trait_list):
        study_list = [study for _ in trait_list]
        data_dict = {'study':study_list, 'trait': trait_list}
        df = pd.DataFrame(data_dict)
        df.to_hdf(self.metafile,
                  key="study_trait",
                  format='table',
                  mode='a',
                  append=True,
                  data_columns=list(df.columns.values),
                  index=False)
        with tb.open_file(self.metafile, "a") as hdf:
            col = hdf.root['study_trait'].table.cols._f_col('study')
            col.remove_index()
            col.create_index(optlevel=6, kind="medium")
            col = hdf.root['study_trait'].table.cols._f_col('trait')
            col.remove_index()
            col.create_index(optlevel=6, kind="medium")

    def load_study_filename(self, study, filename):
        data_dict = {'study': [study], 'file_id': [filename]}
        df = pd.DataFrame(data_dict)
        df.to_hdf(self.metafile,
                  key="study",
                  format='table',
                  mode='a',
                  append=True,
                  data_columns=list(df.columns.values),
                  index=False)
        with tb.open_file(self.metafile, "a") as hdf:
            col = hdf.root['study'].table.cols._f_col('study')
            col.remove_index()
            col.create_index(optlevel=6, kind="medium")


    """ SELECT STATEMENTS """


    def get_chr_pos(self, snp):
        data = []
        search_string = "variant_id == {snp}".format(snp=snp)
        with pd.HDFStore(self.metafile) as store:
            results = store.select('snp', where=search_string)
            if not results.empty:
                data.append((results['chromosome'].values[0], results['base_pair_location'].values[0]))
        return data


    def get_studies(self):
        data = []
        with pd.HDFStore(self.metafile) as store:
            results = store.select('study_trait')
            data.extend(results['study'].tolist())
        if data:
            return data
        else:
            return False

    def get_traits(self):
        data = []
        with pd.HDFStore(self.metafile) as store:
            results = store.select('study_trait')
            data.extend(results['trait'].tolist())
        if data:
            return data
        else:
            return False

    def get_studies_for_trait(self, trait):
        data = []
        search_string = "trait == {trait}".format(trait=trait)
        with pd.HDFStore(self.metafile) as store:
            results = store.select('study_trait', where=search_string)
            data.extend(results['study'].tolist())
        return data

    def get_traits_for_study(self, study):
        data = []
        search_string = "study == {study}".format(study=study)
        with pd.HDFStore(self.metafile) as store:
            results = store.select('study_trait', where=search_string)
            data.extend(results['trait'].tolist())
        return data

    def get_file_id_for_study(self, study):
        data = []
        search_string = "study == {study}".format(study=study)
        with pd.HDFStore(self.metafile) as store:
            results = store.select('study', where=search_string)
            data.extend(results['file_id'].tolist())
        return data


    def get_file_id_for_trait(self, trait):
        data = []
        search_string = "trait == {trait}".format(trait=trait)
        with pd.HDFStore(self.metafile) as store:
            study_list = store.select('study_trait', where=search_string)['study'].tolist()
            if study_list:
                for study in study_list:
                    search_string = "study == {study}".format(study=study)
                    data.extend(store.select('study', where=search_string)['file_id'].tolist())
        return data

    #""" OTHER STATEMENTS """

    #def commit(self):
    #    self.cur.execute("COMMIT")

    #def drop_rsid_index(self):
    #    self.cur.execute("DROP INDEX rsid_idx")

    #def create_rsid_index(self):
    #    self.cur.execute("CREATE INDEX rsid_idx on snp (rsid)")