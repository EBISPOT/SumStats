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
