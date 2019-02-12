import sqlite3


class sqlClient():
    def __init__(self, database):
        self.database = database
        print(self.database)
        self.conn = self.create_conn()
        self.cur = self.conn.cursor()

    def create_conn(self):
        try:
            conn = sqlite3.connect(self.database)
            return conn
        except NameError as e:
            print(e)
        return None

    def insert_snp_row(self, data):
        self.cur.execute('insert or ignore into snp values (?,?,?)', data)

    def drop_rsid_index(self):
        self.cur.execute("DROP INDEX rsid_idx")

    def create_rsid_index(self):
        self.cur.execute("CREATE INDEX rsid_idx on snp (rsid)")


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
        for row in self.cur.execute("SELECT study FROM study"):
            data.append(row[0])
        if data:
            return data
        else:
            return False

    def get_traits(self):
        data = []
        for row in self.cur.execute("SELECT trait FROM trait"):
            data.append(row[0])
        if data:
            return data
        else:
            return False