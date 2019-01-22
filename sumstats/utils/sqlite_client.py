import sqlite3

from sumstats.utils.properties_handler import properties


class sqlClient(object):
    def __init__(self):
        self.database = properties.sqlite_path
        conn = self.create_conn()
        self.cur = conn.cursor()

    def create_conn(self):
        try:
            conn = sqlite3.connect(self.database)
            return conn
        except NameError as e:
            print(e)
        return None



    def check_orientation_with_dbsnp(self, rsid):

        self.cur.execute("SELECT strand FROM snp150Common WHERE name=?", (rsid,))
        data = cur.fetchone()
        if data is not None:
            return data[0]
        return False

    def bp_from_rsid(self, rsid):
        conn = self.create_conn()
        cur = conn.cursor()
        cur.execute("SELECT chrom, chromEnd FROM snp150Common WHERE name=?", (rsid,))
        data = cur.fetchone()
        if data is not None:
            return data
        else:        
            return False

    def insert_snp_row(self, data):
        self.cur.execute('insert or ignore into snp values (?,?,?)', data)

    def drop_index(self, index_name):
        self.cur.execute('DROP INDEX "{0}"'.format(index_name))

    def create_index(self, index_name, table, col):
        self.cur.execute('CREATE INDEX "{0}" on "{1}" ({2})'.format(index_name, table, col))

    def commit(self):
        self.cur.execute("COMMIT")


    def get_chr_pos(self, snp):
        data = []
        for row in self.cur.execute("SELECT chr, position FROM snp WHERE rsid=?", (snp,)):
            data.append(row)
        if data:
            return data
        else:
            return False
