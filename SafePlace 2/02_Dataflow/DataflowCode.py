#Dataflow EDEM Code

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

    #Add Processing Time (new column)
    row["processingTime"] = str(datetime.datetime.now())

    #Return function
    return row

class add_processing_time(beam.DoFn):
    def process(self, element):
        window_start = str(datetime.datetime.now())
        output_data = {'id_persona': element, 'processingTime': window_start}
        output_json = json.dumps(output_data)
        yield output_json.encode('utf-8')

class agg_id_persona(beam.DoFn):
    def process(self, element):
        temp = element['id_persona']
        yield temp

#Create Beam pipeline

def edemData(output_table):

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
            p | "Read messages from PubSub" >> beam.io.ReadFromPubSub(subscription=f"projects/cobalt-diorama-337709/subscriptions/{output_table}-sub", with_attributes=True)
            #Parse JSON messages with Map Function and adding Processing timestamp
              | "Parse JSON messages" >> beam.Map(parse_json_message)
        )

        #Part02: Write proccessing message to their appropiate sink
        #Data to Bigquery
        (data | "Write to BigQuery" >> beam.io.WriteToBigQuery(
            table = f"cobalt-diorama-337709:edemDataset.{output_table}",
            schema = schema,
            create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
            write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND
        ))

        #Part03: Count id_persona per minute and put that data into PubSub

        #Create a fixed window (1 min duration)
        (data 
            | "Get id_persona value" >> beam.ParDo(agg_id_persona())
            | "WindowByMinute" >> beam.WindowInto(window.FixedWindows(60))
            | "MeanByWindow" >> beam.CombineGlobally(MeanCombineFn()).without_defaults()
            | "Add Window ProcessingTime" >> beam.ParDo(add_processing_time())
            | "WriteToPubSub" >> beam.io.WriteToPubSub(topic="projects/cobalt-diorama-337709/topics/iotToCloudFunctions", with_attributes=False)
        )

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    edemData("iotToBigQuery")