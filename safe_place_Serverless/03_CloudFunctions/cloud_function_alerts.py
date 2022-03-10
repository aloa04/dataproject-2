# -*- coding: utf-8 -*-
"""
Created on Tue Mar  8 22:31:00 2022

@author: Ismail
"""

# Cloud Function triggered by PubSub Event
# When a temperature over 23ºC or under 17ºC is received, a IoT Core command will be throw.

# Import libraries
from datetime import datetime
from google.cloud import bigquery
import base64, json, sys, os
import google.cloud.logging
import logging

# Read from PubSub
def alert(event, context):
    client = google.cloud.logging.Client()
    client.setup_logging()

    # Read message from Pubsub (decode from Base64)
    pubsub_message = base64.b64decode(event['data']).decode('utf-8')

    # Load json
    message = json.loads(pubsub_message)

    # Lo ponemos todo en un log
    logging.info(message) 
    logging.debug(message)


    # Ahora que tenemos los datos como message
    print('MESSAge: ', message)
    TABLE_READ = "safeplaceid.safeplacedb.iotToBigQuery" #poner las tablas 
    TABLE_DESTINATION ="safeplaceid.safeplacedb.alertas" #poner las tablas

    def parse_time(timestamp):
        return datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f') # pasa de timestamp a datetime porque el timestamp no es comprenhensible par el ser humano 

    # Construct a BigQuery client object.
    client = bigquery.Client()
    """ READ BIGQUERY STATUS""" 
    q = f"""SELECT id_persona, Max(timestamp) as tiempo  FROM `{TABLE_READ}` where device_id = 'bano1' group by id_persona Having count(*)%2 = 1""" # Aquí estamos creando una consulta sql y poniendola en la variable q
    df = (client.query(q).result().to_dataframe()) # Ejecuta la consulta "q" con el cliente que hemos creado antes, todo esto se mete en la variable "df"

    df['tiempo'] = df['tiempo'].apply(parse_time)
    
    timespent = df['tiempo'] - datetime.now()
    timespent1 = datetime(year=2020, month=1, day=1, hour=0, minute=8, second=0)
    timespent2 = datetime(year=2020, month=1, day=1, hour=0, minute=1, second=0)
    timedelta = timespent - timespent2
    
    if (timespent > timedelta):
        status = [{'sensor_id': 'bano1',
                    'id_persona': df['id_persona'],
                    'tiempo': df['tiempo']
                  }]
        bq_client = bigquery.Client()

        table = bq_client.get_table(TABLE_DESTINATION)
        errors = bq_client.insert_rows_json(table, status)
        if errors == []:
            logging.info(" #~#~#~#~#~#~# SUCCESS #~#~#~#~#~#~#")
        else:
            logging.info(" #~#~#~#~#~#~# FALLO #~#~#~#~#~#~#")