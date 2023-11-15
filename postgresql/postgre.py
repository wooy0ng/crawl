import os
import psycopg2
import json
from pathlib import Path
from typing import List, Optional

user_config_path = f"{Path(__file__).parent}/postgre_user_config.json"


class Databases():
    def __init__(self, dbname):
        if not os.path.exists(user_config_path):
            raise FileNotFoundError("postgre_user_config.json 파일이 없습니다.")
        
        with open(user_config_path, "r") as f:
            conf = json.load(f)
        
        self.db = psycopg2.connect(
            host=conf["host"], 
            dbname=dbname,
            user=conf["user"],
            password=conf["password"],
            port=conf["port"]
        )
        
        self.cursor = self.db.cursor()

    def __del__(self):
        self.db.close()
        self.cursor.close()

    def execute(self,query,args={}):
        self.cursor.execute(query,args)
        row = self.cursor.fetchall()
        return row

    def commit(self):
        self.cursor.commit()
        
        
class CRUD(Databases):
    def make_columns_query(self, columns: List[str]):
        columns_sql = ""
        for column in columns:
            columns_sql += f"{column}, " 
        return columns_sql[:-2]
    
    def make_values_query(self, values: List[str]):
        values_sql = ""
        for value in values:
            values_sql += f"$${value}$$, "
        return values_sql[:-2]
    
    def transaction(self, sql) -> Optional[str]:
        result = None
        try:
            self.cursor.execute(sql)
            if "SELECT" in sql:
                result = self.cursor.fetchall()
            self.db.commit()
        except Exception as e:
            print(e)
            self.db.rollback()
        return result
        
    def insertDB(self, table: str, columns: List[str], values: List[str]):    
        """
        example:
            INSERT INTO crawl (title, content, url, user_t, user_c, detection_time, label) 
                    VALUES ('a', 'b', 'c', 'd', 'e', 'f', 'g');
        """
        sql = f"INSERT INTO {table}({self.make_columns_query(columns)}) VALUES ({self.make_values_query(values)});"
        self.transaction(sql)
    
    def readDB(self, table, columns:List[str], condition:Optional[str]=None):
        """ 
        example:
            SELECT title, content FROM crawl;
        """
        sql = f"SELECT {self.make_columns_query(columns)} from {table}"
        if condition:
            sql += f" WHERE {condition}"
        result = self.transaction(sql)
        return result

    def updateDB(self, table, columns:List[str], values:List[str], condition: Optional[str]=None):
        """ 
        example:
            UPDATE crawl SET title='none', url='none' WHERE title='title'
        """
        set_query = ""
        for column, value in zip(columns, values):
            set_query += f"{column}='{value}', " if type(value) == str else f"{column}={value}, "
        set_query = set_query[:-2]
        
        sql = f"UPDATE {table} SET {set_query}"
        if condition:
            sql += f" WHERE {condition}"
        self.transaction(sql)

    def deleteDB(self, table, condition: Optional[str]=None):
        """ 
            example : DELETE FROM testtable WHERE id='test';
        """
        sql = f"DELETE FROM {table}"
        if condition:
            sql += f" WHERE {condition}"    
        self.transaction(sql)


if __name__ == "__main__":
    db = CRUD(dbname='postgres')
    db.insertDB(
        table='crawl',
        columns=['title', 'content', 'url', 'user_t', 'user_c', 'detection_time'], 
        values=['title', 'content', 'url', 'user_t', 'user_c', '000000']
    )
    db.insertDB(
        table='crawl',
        columns=['title', 'content', 'url', 'user_t', 'user_c', 'detection_time'], 
        values=['title', 'content', 'url1', 'user_t', 'user_c', '000001']
    )
    
    print(db.readDB(table='crawl', columns=['title', 'content', 'url', 'user_t', 'user_c', 'detection_time']))
    db.updateDB(table='crawl', columns=['title'], values=['와우'], condition="url='url'")
    
    db.deleteDB(table='crawl', condition="detection_time='000001'")
    db.deleteDB(table='crawl')
    
    
