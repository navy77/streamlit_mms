import utils.constant as constant
import os

from utils.influx_to_sqlserver import INFLUX_TO_SQLSERVER
from utils.mc_status_to_sqlserver import MCSTATUS
from utils.alarmlist_to_sqlserver import ALARMLIST

from dotenv import load_dotenv

load_dotenv()


project_type_1 = os.environ["PROJECT_TYPE_1"]
project_type_2 = os.environ["PROJECT_TYPE_2"]
project_type_3 = os.environ["PROJECT_TYPE_3"]

try:
    # if project_type_1 == "PRODUCTION":
    #     influx_to_sqlserver = INFLUX_TO_SQLSERVER(
    #         server=os.getenv('SERVER'),
    #         database=os.getenv('DATABASE'),
    #         user_login=os.getenv('USER_LOGIN'),
    #         password=os.getenv('PASSWORD'),
    #         table=os.getenv('TABLE_1'),
    #         table_columns=os.getenv('PRODUCTION_TABLE_COLUMNS'),
    #         table_log=os.getenv('TABLE_LOG_1'),
    #         table_columns_log=os.getenv('TABLE_COLUMNS_LOG'),
    #         initial_db=os.getenv('INITIAL_DB'),

    #         influx_server=os.getenv('INFLUX_SERVER'),
    #         influx_database=os.getenv('INFLUX_DATABASE'),
    #         influx_user_login=os.getenv('INFLUX_USER_LOGIN'),
    #         influx_password=os.getenv('INFLUX_PASSWORD'),
    #         column_names=os.getenv('COLUMN_NAMES'),
    #         mqtt_topic=os.getenv('MQTT_TOPIC_1'),

    #         line_notify_token=os.getenv('LINE_NOTIFY_TOKEN'),
    #         line_notify_flag=os.getenv('LINE_NOTIFY_FLAG'),
            
    #     )
    #     influx_to_sqlserver.run()

    if project_type_2 == "MCSTATUS":
        mcstatus_to_sqlserver = MCSTATUS(
            server=os.getenv('SERVER'),
            database=os.getenv('DATABASE'),
            user_login=os.getenv('USER_LOGIN'),
            password=os.getenv('PASSWORD'),
            table=os.getenv('TABLE_2'),
            table_columns=os.getenv('MCSTATUS_TABLE_COLUMNS'),
            table_log=os.getenv('TABLE_LOG_2'),
            table_columns_log=os.getenv('TABLE_COLUMNS_LOG'),
            initial_db=os.getenv('INITIAL_DB'),

            influx_server=os.getenv('INFLUX_SERVER'),
            influx_database=os.getenv('INFLUX_DATABASE'),
            influx_user_login=os.getenv('INFLUX_USER_LOGIN'),
            influx_password=os.getenv('INFLUX_PASSWORD'),
            mqtt_topic=os.getenv('MQTT_TOPIC_2'),

            line_notify_token=os.getenv('LINE_NOTIFY_TOKEN'),
            line_notify_flag=os.getenv('LINE_NOTIFY_FLAG'),
            
        )
        mcstatus_to_sqlserver.run()

    if project_type_3 == "ALARMLIST":
        alarmlist_to_sqlserver = ALARMLIST(
            server=os.getenv('SERVER'),
            database=os.getenv('DATABASE'),
            user_login=os.getenv('USER_LOGIN'),
            password=os.getenv('PASSWORD'),
            table=os.getenv('TABLE_3'),
            table_columns=os.getenv('ALARMLIST_TABLE_COLUMNS'),
            table_log=os.getenv('TABLE_LOG_3'),
            table_columns_log=os.getenv('TABLE_COLUMNS_LOG'),
            initial_db=os.getenv('INITIAL_DB'),

            influx_server=os.getenv('INFLUX_SERVER'),
            influx_database=os.getenv('INFLUX_DATABASE'),
            influx_user_login=os.getenv('INFLUX_USER_LOGIN'),
            influx_password=os.getenv('INFLUX_PASSWORD'),
            mqtt_topic=os.getenv('MQTT_TOPIC_3'),

            line_notify_token=os.getenv('LINE_NOTIFY_TOKEN'),
            line_notify_flag=os.getenv('LINE_NOTIFY_FLAG'),
        )
        alarmlist_to_sqlserver.run()

    else:
        print("ERROR: UNKNOWN PROJECT TYPE!")
except Exception as e:
    print(e)
    