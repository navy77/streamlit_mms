import utils.constant as constant
import pandas as pd
import os
import sys
import utils.alert as alert
import pymssql
import json

from datetime import datetime,date, timedelta
from sqlalchemy import create_engine,text,engine
from influxdb import InfluxDBClient
from datetime import datetime

class PREPARE:

    def __init__(self,server,database,user_login,password,table,table_columns,table_log,table_columns_log,line_notify_token,influx_server,influx_database,influx_user_login,influx_password,mqtt_topic,initial_db,line_notify_flag):
        self.server = server
        self.database = database
        self.user_login = user_login
        self.password = password
        self.table_log = table_log
        self.table = table
        self.table_columns = table_columns
        self.table_columns_log = table_columns_log
        self.df_insert = None
        self.df_influx = None
        self.df_sql = None
        self.line_notify_token = line_notify_token
        self.influx_server = influx_server
        self.influx_database = influx_database
        self.influx_user_login = influx_user_login
        self.influx_password = influx_password

        self.mqtt_topic = mqtt_topic
        self.initial_db = initial_db
        self.line_notify_flag = line_notify_flag

    def stamp_time(self):
        now = datetime.now()
        print("\nHi this is job run at -- %s"%(now.strftime("%Y-%m-%d %H:%M:%S")))

    def error_msg(self,process,msg,e):
        result = {"status":constant.STATUS_ERROR,"process":process,"message":msg,"error":e}

        try:
            print("Error: "+self.alert_error_msg(result))
            if self.line_notify_flag == "True":
                self.alert_line(self.alert_error_msg(result))
            self.log_to_db(result)
            sys.exit()
        except Exception as e:
            self.info_msg(self.error_msg.__name__,e)
            sys.exit()
    
    def alert_line(self,msg):
        value = alert.line_notify(self.line_notify_token,msg)
        value = json.loads(value)  
        if value["message"] == constant.STATUS_OK:
            self.info_msg(self.alert_line.__name__,'sucessful send to line notify')
        else:
            self.info_msg(self.alert_line.__name__,value)

    def alert_error_msg(self,result):
        if self.line_notify_token != None:
            return f'\nproject: {self.table}\nprocess: {result["process"]}\nmessage: {result["message"]}\nerror: {result["error"]}\n'
                
    def info_msg(self,process,msg):
        result = {"status":constant.STATUS_INFO,"process":process,"message":msg,"error":"-"}
        print(result)

    def ok_msg(self,process):
        result = {"status":constant.STATUS_OK,"process":process,"message":"program running done","error":"-"}
        try:
            self.log_to_db(result)
            print(result)
        except Exception as e:
            self.error_msg(self.ok_msg.__name__,'cannot ok msg to log',e)
    
    def conn_sql(self):
        #connect to db
        try:
            cnxn = pymssql.connect(self.server, self.user_login, self.password, self.database)
            cursor = cnxn.cursor()
            return cnxn,cursor
        except Exception as e:
            self.alert_line("Danger! cannot connect sql server")
            self.info_msg(self.conn_sql.__name__,e)
            sys.exit()

    def log_to_db(self,result):
        #connect to db
        cnxn,cursor=self.conn_sql()
        try:
            cursor.execute(f"""
                INSERT INTO [{self.database}].[dbo].[{self.table_log}] 
                values(
                    getdate(), 
                    '{result["status"]}', 
                    '{result["process"]}', 
                    '{result["message"]}', 
                    '{str(result["error"]).replace("'",'"')}'
                    )
                    """
                )
            cnxn.commit()
            cursor.close()
        except Exception as e:
            self.alert_line("Danger! cannot insert log table")
            self.info_msg(self.log_to_db.__name__,e)
            sys.exit()


class MCSTATUS(PREPARE):

    def __init__(self,server,database,user_login,password,table,table_columns,table_log,table_columns_log,influx_server,influx_database,influx_user_login,influx_password,mqtt_topic,initial_db,line_notify_flag,line_notify_token=None):
        super().__init__(server,database,user_login,password,table,table_columns,table_log,table_columns_log,line_notify_token,influx_server,influx_database,influx_user_login,influx_password,mqtt_topic,initial_db,line_notify_flag)      
    
    def query_influx(self) :
        try:
            result_lists = []
            client = InfluxDBClient(self.influx_server, 8086, self.influx_user_login,self.influx_password, self.influx_database)
            mqtt_topic_value = list(str(self.mqtt_topic).split(","))
            for i in range(len(mqtt_topic_value)):
                query = f"select status,topic,yyyy,mm,dd,hh,min,sec from mqtt_consumer where topic ='{mqtt_topic_value[i]}' order by time desc limit 10"
                result = client.query(query)
                result_df = pd.DataFrame(result.get_points())
                result_lists.append(result_df)
            query_influx = pd.concat(result_lists, ignore_index=True)
            self.df_influx = query_influx 
        except Exception as e:
            self.error_msg(self.lastone.__name__,"cannot query influxdb",e)

    def edit_col(self):
            try:
                df = self.df_influx.copy()
                df_split = df['topic'].str.split('/', expand=True)
                df['mc_no'] = df_split[3].values
                df['process'] = df_split[2].values
                df.drop(columns=['topic'],inplace=True)
                df.rename(columns = {'time':'data_timestamp'}, inplace = True)
                df["data_timestamp"] =   pd.to_datetime(df["data_timestamp"]).dt.tz_convert(None)
                df["data_timestamp"] = df["data_timestamp"] + pd.DateOffset(hours=7)    
                df["data_timestamp"] = df['data_timestamp'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])
                df["occurred"] = df['yyyy'].astype(int).astype(str)+ '-' +  df['mm'].astype(int).astype(str)+ '-' +  df['dd'].astype(int).astype(str)+ '-' +  df['hh'].astype(int).astype(str)+ '-' +  df['min'].astype(int).astype(str)+ '-' +  df['sec'].astype(int).astype(str)
                df["occurred"] = pd.to_datetime(df["occurred"], format="%Y-%m-%d-%H-%M-%S")
                df["occurred"] = df['occurred'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S'))
                df.drop(columns=['yyyy'],inplace=True)
                df.drop(columns=['mm'],inplace=True)
                df.drop(columns=['dd'],inplace=True)
                df.drop(columns=['hh'],inplace=True)
                df.drop(columns=['min'],inplace=True)
                df.drop(columns=['sec'],inplace=True)
                df.rename(columns={'status': 'mc_status'}, inplace=True)
                self.df_influx = df
            except Exception as e:
                self.error_msg(self.edit_col.__name__,"cannot edit dataframe data",e)

    def query_sql(self):
        try:
            engine1 = create_engine(f'mssql+pymssql://{self.user_login}:{self.password}@{self.server}/{self.database}')
            sql_query = f"""SELECT TOP 20 * FROM [{self.database}].[dbo].[{self.table}] ORDER by registered_at desc"""
           
            df_sql = pd.read_sql(sql_query, engine1)
            df_sql.rename(columns={'registered_at': 'data_timestamp'}, inplace=True)
            columns = df_sql.columns.tolist()
            new_order = [columns[0], columns[2], columns[3],columns[4], columns[1]]
            df_sql = df_sql[new_order]
            return df_sql
        except Exception as e:
                self.error_msg(self.query_df.__name__,"cannot select with sql code",e)
 
    def check_duplicate(self):
        try:
            df_from_influx = self.df_influx
            df_from_sql = self.query_sql()         
            df_from_influx['occurred'] = pd.to_datetime(df_from_influx['occurred'])
            # df_from_influx.drop(columns=['data_timestamp'],inplace=True)
            df_from_sql['occurred'] = pd.to_datetime(df_from_sql['occurred'])
            # df_from_sql.drop(columns=['data_timestamp'],inplace=True)
            
            df_right_only = pd.merge(df_from_sql,df_from_influx , on = ["occurred","mc_no","mc_status","process"], how = "right", indicator = True) 
            df_right_only = df_right_only[df_right_only['_merge'] == 'right_only'].drop(columns=['_merge'])
            if df_right_only.empty:              
                self.info_msg(self.check_duplicate.__name__,f"data is not new for update")
            else:
                self.info_msg(self.check_duplicate.__name__,f"we have data new")
                self.df_insert = df_right_only       
            return constant.STATUS_OK    
        except Exception as e:
            self.error_msg(self.check_duplicate.__name__,"cannot select with sql code",e)
    
    def df_to_db(self):
        #connect to db
        mcstatus_list = ['occurred','mc_status','mc_no','process']
        cnxn,cursor=self.conn_sql()
        try:
            df = self.df_insert
            for index, row in df.iterrows():
                value = None
                for i in range(len(mcstatus_list)):
                    address = mcstatus_list[i]
                    if value == None:
                        value = ",'"+str(row[address])+"'"
                    else:
                        value = value+",'"+str(row[address])+"'"
                
                insert_string = f"""
                INSERT INTO [{self.database}].[dbo].[{self.table}] 
                values(
                    getdate()
                    {value}
                    )
                    """
                cursor.execute(insert_string)
                cnxn.commit()
            cursor.close()
            self.df_insert = None

            self.info_msg(self.df_to_db.__name__,f"insert data successfully")     
        except Exception as e:
            print('error: '+str(e))
            self.error_msg(self.df_to_db.__name__,"cannot insert df to sql",e)

    def run(self):
        self.stamp_time()
        if self.initial_db == 'True':
            self.query_influx()
            self.edit_col()
            self.query_sql()
            self.check_duplicate()
            if self.check_duplicate() == constant.STATUS_OK:
                self.df_to_db()
            self.ok_msg(self.df_to_db.__name__)

if __name__ == "__main__":
    print("must be run with main")
