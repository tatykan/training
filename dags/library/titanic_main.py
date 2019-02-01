
import pandas as pd
import psycopg2
from io import StringIO

class connection():
    def __init__(self, host, dbname, user, password):
        self.host = host
        self.dbname = dbname
        self.user = user
        self.password = password
        self.conn = psycopg2.connect(' '.join(['host='+str(host),
                                  'dbname='+str(dbname),
                                  'user='+str(user),
                                  'password='+str(password)]))
    def create_table(self, table, data):
        self.data = data
        self.table = table
        self.key = {'object':'varchar',
           'int64':'int',
           'float64':'float',
           'datetime64[ns]':'date',
           'bool':'boolean'
           }
        
        def create_dict(df):
            dct = {}
            for n,i in enumerate(df.dtypes):
                dct[df.columns[n]] = [str(i),str(max([len(x) for x in df[df.columns[n]].astype(str)]))]
            return dct
        
        self.dct = create_dict(self.data)
        self.create = "DROP TABLE IF EXISTS "+self.table+" CASCADE; CREATE TABLE "+self.table+"("+ \
            ', '.join([item+' '+self.key[self.dct[item][0]]+'('+self.dct[item][1]+')' 
            if ((self.key[self.dct[item][0]]!='date')&(self.key[self.dct[item][0]]!='int')) 
            else item+' '+self.key[self.dct[item][0]] for item in self.data.columns]) \
            +');'
        with self.conn.cursor() as c:
            c.execute(self.create)
            self.conn.commit()
    
    def fill_table(self, table, data):
        self.table = table
        self.data = data
        self.sio = StringIO()
        self.sio.write(self.data.to_csv(index=None, header=None))
        self.sio.seek(0)
        with self.conn.cursor() as c:
            c.copy_from(self.sio, self.table, columns=self.data.columns, sep=',')
            self.conn.commit()
    
    def query_table(self, query, columns):
        self.columns = columns
        self.query = query
        with self.conn.cursor() as c:
            c.execute(self.query)
            self.data = c.fetchall()
        self.df = pd.DataFrame(self.data, columns=self.columns)
    
    def close_connection(self):
        self.conn.close()