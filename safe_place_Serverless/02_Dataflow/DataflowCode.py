#Import Libraries

import argparse
import json
import logging
import time
import apache_beam as beam
from apache_beam.options.pipeline_options import (PipelineOptions, StandardOptions)
from apache_beam.transforms.combiners import MeanCombineFn
from apache_beam.transforms.combiners import CountCombineFn
from apache_beam.transforms.core import CombineGlobally
import apache_beam.transforms.window as window
from apache_beam.io.gcp.bigquery import parse_table_schema_from_json
from apache_beam.io.gcp import bigquery_tools
import datetime


#ParseJson Function

#Get data from PubSub and parse them

def parse_json_message(message):
    #Mapping message from PubSub
    #DecodePubSub message in order to deal with
    pubsubmessage = message.data.decode('utf-8')
    #Get messages attributes
    attributes = message.attributes

    #Print through console and check that everything is fine.
    logging.info("Receiving message from PubSub:%s", message)
    logging.info("with attributes: %s", attributes)

    #Convert string decoded in json format(element by element)
    row = json.loads(pubsubmessage)

    #Return function
    return row

class parse_json(beam.DoFn):
    def process(self, element):
        output_json = json.dumps(element)
        yield output_json.encode('utf-8')


#Create Beam pipeline

def deviceActions(output_table):

    #Load schema from BigQuery/schemas folder
    with open(f"schemas/{output_table}.json") as file:
        input_schema = json.load(file)
    
    #Declare bigquery schema
    schema = bigquery_tools.parse_table_schema_from_json(json.dumps(input_schema))

    #Create pipeline
    #First of all, we set the pipeline options
    options = PipelineOptions(save_main_session=True, streaming=True)
    with beam.Pipeline(options=options) as p:

        #Part01: we create pipeline from PubSub to BigQuery

        data = (
            #Read messages from PubSub
            p | "Read messages from PubSub" >> beam.io.ReadFromPubSub(subscription=f"projects/safeplaceid/subscriptions/{output_table}-sub", with_attributes=True)
            #Parse JSON messages with Map Function and adding Processing timestamp
              | "Parse JSON messages" >> beam.Map(parse_json_message)
        )
        

        #Part02: Write proccessing message to their appropiate sink
        #Data to Bigquery
        (data | "Write to BigQuery" >> beam.io.WriteToBigQuery(
            table = f"safeplaceid:safeplacedb.{output_table}",
            schema = schema,
            create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
            write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND
        ))

        # Part03: Publish data to CloudFunctions topic
        
        (data
            | "Parse JSON" >> beam.ParDo(parse_json())
            | "Write to CF topic" >> beam.io.WriteToPubSub(topic=f"projects/safeplaceid/topics/iotToCloudFunctions", with_attributes=False)
         )



if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    deviceActions("iotToBigQuery")
