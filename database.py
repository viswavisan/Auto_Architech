import pymysql
class sql_query:
    def __init__(self):
        self.host='localhost'
        self.user='root'
        self.password=''
        self.port='0'
        self.db='test_db'
                
        
    def connect(self):
        try:return pymysql.connect(host=self.host,user=self.user,password=self.password,port=int(self.port),db=self.db,charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
        except Exception: return 'connectivity error'
    def insert(self,table,d):
        sql=self.connect()
        cursor=  sql.cursor()
        keys=','.join([k or '' for k in d.keys()]);values="','".join([str(v) for v in d.values()])
        x=cursor.execute(f"INSERT ignore INTO {table}  ({keys}) VALUES('{values}')");sql.commit();sql.close()
        return x
    def insertmany(self,table,ds):
        sql=self.connect()
        cursor=  sql.cursor()
        keys=','.join([k or '' for k in ds[0].keys()]);
        values=','.join([str(tuple(d.values())) for d in ds])
        x=cursor.execute(f"INSERT ignore INTO {table}  ({keys}) VALUES {values}");sql.commit();sql.close()
        return x
    def update(self,table,d,where):
        sql=self.connect() 
        cursor=  sql.cursor()
        fields=",".join([f"{k}='{v or ''}'" for k,v in d.items()])
        x=cursor.execute(f"UPDATE {table}  SET {fields} {where}")
        sql.commit();sql.close();return x
    def getdatas(self,query):
        sql=self.connect()
        cursor=  sql.cursor();self.affect=cursor.execute(query)
        x=cursor.fetchall();sql.close();return x
    def getdata(self,query):
        sql=self.connect()
        cursor=  sql.cursor();self.affect=cursor.execute(query)
        x=cursor.fetchone();sql.close();return x

sql=sql_query()