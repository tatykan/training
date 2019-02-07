
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
        
        def get_length(df, column):
            return str(max([len(str(x)) for x in df[column]]))

        def get_type(df, column):
            return self.key[str(df[column].dtypes)]
        
        self.drop = "DROP TABLE IF EXISTS "+self.table+" CASCADE;"
        self.create = "CREATE TABLE "+self.table+"("+ \
                ', '.join([column +' '+ get_type(self.data, column) +'({})'.format(get_length(self.data, column)) \
                if (get_type(self.data, column)!='date')&(get_type(self.data, column)!='int') \
                else column +' '+ get_type(self.data, column) \
                for column in self.data.columns]) +');'
        self.statement = ' '.join([self.drop, self.create])
        with self.conn.cursor() as c:
            c.execute(self.statement)
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