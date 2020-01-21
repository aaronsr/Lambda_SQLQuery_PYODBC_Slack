import pyodbc
import datetime
import json
import time
import collections
import requests
from pprint import pprint as pp


query = "SELECT TOP (5) [DatabaseLogID], [PostTime], [DatabaseUser], " \
        "[Event] FROM [AdventureWorks2017].[dbo].[DatabaseLog]"

query2 = """
    BACKUP DATABASE [AdventureWorks2017] 
    TO  DISK = N'C:\TEST\AdventureWorks.bak' 
    WITH NOFORMAT, NOINIT,  
    NAME = N'AdventureWorks2017-Full Database Backup', 
    SKIP, NOREWIND, NOUNLOAD,  STATS = 10
"""

query3 = """
    SELECT TOP (1000) [backup_set_id]
      ,[name]
      ,[backup_start_date]
      ,[backup_finish_date]
      ,[backup_size]
      ,[database_name]
      ,[server_name]
      ,[machine_name]
      ,[recovery_model]
      FROM [msdb].[dbo].[backupset]
      where database_name = 'AdventureWorks2017' AND backup_finish_date >= DATEADD(hh, -2, GETDATE())
      order by backup_finish_date desc
"""

query4 = """
    select h.server as [Server],
        j.[name] as [Name],
        h.message as [Message],
        h.run_date as LastRunDate, 
        h.run_time as LastRunTime
    from sysjobhistory h
        inner join sysjobs j on h.job_id = j.job_id
            where j.enabled = 1 
            and h.instance_id in
            (select max(h.instance_id)
                from sysjobhistory h group by (h.job_id))
            and h.run_status = 0
"""

query6 = """
    CREATE PROCEDURE dbo.doShrinkAndBackup
    AS
    BEGIN
        SET NOCOUNT ON;
    
        DBCC SHRINKFILE(myDb_log, 100);
    
        BACKUP DATABASE myDb
        TO  DISK = N'C:\__tmp\myDb.bak' WITH NOFORMAT
        ,   INIT
        ,   NAME = N'myDb backup', SKIP, REWIND, NOUNLOAD
        ,   STATS = 10;
    END
"""


def date_time_converter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()


def post_message_to_slack(text, blocks=None):
    res = requests.post(slack_webhook_url, json={
        'channel': slack_channel,
        'text': text,
        'username': slack_user_name,
        'blocks': blocks if blocks else None
    })


def lambda_handler(event, context):
    try:
        # Runs a sql backup
        backup_sql_database(event['server'], event['database'], event['username'], event['password'])

        # Checks the SQL backup status.
        backup_status = backup_job_status(event['server'], 'msdb', event['username'], event['password'], query3)

        #  Runs a random SQL query
        results = run_sql_query(event['server'], 'msdb', event['username'], event['password'], query4)
        server = results[1]['Server']
        name = results[1]['Name']
        message = results[1]['Message']
        lastrundate = results[1]['LastRunDate']
        lastruntime = results[1]['LastRunTime']

        block = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Job Failure: * Action required"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": "*Server:*\n{}".format(server)
                    },
                    {
                        "type": "mrkdwn",
                        "text": "*Job Name:* \n{}".format(name)
                    },
                    {
                        "type": "mrkdwn",
                        "text": "*Last Run:* \n{}".format(lastrundate)
                    },
                    {
                        "type": "mrkdwn",
                        "text": "*Run Time:* \n{}".format(lastruntime)
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "plain_text",
                    "text": str(message),
                    "emoji": False
                }
            }
        ]

        post_message_to_slack(message, block)

    except Exception as error:
        return error


def backup_job_status(server, database, username, password, qry):
    results = []
    while results is False:
        results = run_sql_query(server, database, username, password, qry)
        print("results are false")
        time.sleep(5)
    else:
        return "backup complete"


def restore_sql_database():
    pass


def backup_sql_database(server, database, username, password):
    try:
        connection = connect_to_sql(server, database, username, password)
        connection.autocommit = True
        cursor = connection.cursor()
        cursor.execute(query2)
        while cursor.nextset():
            pass
        for row in cursor.fetchall():
            print(row)

    except Exception as e:
        return e


def connect_to_sql(server, database, username, password):
    try:
        connection = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID='
            + username + ';PWD=' + password)
        return connection
    except Exception as e:
        return e


def run_sql_query(server, database, username, password, qry):
    try:
        cnxn = connect_to_sql(server, database, username, password)
        cursor = cnxn.cursor()
        cursor.execute(qry)
        rows = cursor.fetchall()
        objects_list = []
        for row in rows:
            d = collections.OrderedDict()
            d['Server'] = row.Server
            d['Name'] = row.Name
            d['Message'] = row.Message
            d['LastRunDate'] = row.LastRunDate
            d['LastRunTime'] = row.LastRunTime
            objects_list.append(d)
        j = json.dumps(objects_list)
        return objects_list

    except Exception as e:
        return e














