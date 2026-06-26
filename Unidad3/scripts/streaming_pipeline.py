import argparse
import logging
import json
import re
from datetime import datetime
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, SetupOptions
from apache_beam.io.gcp.bigquery import WriteToBigQuery

# Regex to find and replace the last octet of an IPv4 address
IP_MASK_REGEX = re.compile(r'\.\d+$')

class CleanAndAnonymizeFn(beam.DoFn):
    def process(self, element):
        try:
            # Parse the incoming JSON message from Pub/Sub
            data = json.loads(element.decode('utf-8'))
            
            session_id = data.get('session_id')
            raw_timestamp = data.get('timestamp')
            ip_address = data.get('ip_address')
            customer_id = data.get('customer_id')
            event_type = data.get('event_type')
            sku_product = data.get('sku_product')
            device = data.get('device')
            
            # 1. Normalización del Timestamp
            # Pub/Sub messages should have ISO timestamp, e.g. 2024-06-01T14:30:00Z
            # Convert to BigQuery compatible format (YYYY-MM-DD HH:MM:SS)
            formatted_timestamp = None
            if raw_timestamp:
                try:
                    # Strip Z and parse
                    clean_ts = raw_timestamp.replace('Z', '')
                    dt = datetime.fromisoformat(clean_ts)
                    formatted_timestamp = dt.strftime('%Y-%m-%d %H:%M:%S')
                except Exception as ts_err:
                    logging.warning(f"Error parsing timestamp {raw_timestamp}: {ts_err}")
                    formatted_timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            
            # 2. Seudonimización del ID de Cliente (customer_id / RUT)
            # Regla: Primeros 3 caracteres + 'XXXXXX-' + último caracter. Si es nulo, queda NULL
            id_anonimo_cliente = None
            if customer_id and str(customer_id).strip() != "":
                cust_str = str(customer_id).strip()
                if len(cust_str) >= 4:
                    id_anonimo_cliente = f"{cust_str[:3]}XXXXXX-{cust_str[-1]}"
                else:
                    id_anonimo_cliente = f"{cust_str}XXXXXX"
            
            # 3. Anonimización de IP a nivel de subred
            # Regla: Reemplazar el último octeto por .0 (ej: 192.168.1.55 -> 192.168.1.0)
            ip_anonima = None
            if ip_address:
                ip_anonima = IP_MASK_REGEX.sub('.0', ip_address)
            
            # Construct the clean record matching BQ schema
            clean_record = {
                'session_id': session_id,
                'timestamp': formatted_timestamp,
                'ip_anonima': ip_anonima,
                'id_anonimo_cliente': id_anonimo_cliente,
                'event_type': event_type,
                'sku_product': sku_product,
                'device': device
            }
            
            yield clean_record
            
        except Exception as e:
            logging.error(f"Error processing message: {e}. Message content: {element}")

def run(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--input_subscription',
        required=True,
        help='Input Pub/Sub subscription in the format "projects/<PROJECT>/subscriptions/<SUBSCRIPTION>".'
    )
    parser.add_argument(
        '--output_table',
        default='cordillerabi:grupo_cordillera_dw.fact_sesiones_web_streaming',
        help='BigQuery table destination, e.g. "project:dataset.table"'
    )
    parser.add_argument(
        '--write_method',
        default='FILE_LOADS',
        choices=['STREAMING_INSERTS', 'FILE_LOADS'],
        help='BigQuery write method.'
    )
    parser.add_argument(
        '--triggering_frequency',
        type=int,
        default=15,
        help='Triggering frequency in seconds for FILE_LOADS.'
    )
    parser.add_argument(
        '--gcs_temp_location',
        default='gs://grupo-cordillera-datalake-cordillerabi/temp_streaming',
        help='GCS temp location for FILE_LOADS.'
    )
    
    known_args, pipeline_args = parser.parse_known_args(argv)
    
    # We enforce streaming mode for Pub/Sub source
    pipeline_options = PipelineOptions(pipeline_args)
    pipeline_options.view_as(SetupOptions).save_main_session = True
    
    # Configure BQ write method
    write_kwargs = {
        'table': known_args.output_table,
        'schema': 'session_id:STRING,timestamp:TIMESTAMP,ip_anonima:STRING,id_anonimo_cliente:STRING,event_type:STRING,sku_product:STRING,device:STRING',
        'write_disposition': beam.io.BigQueryDisposition.WRITE_APPEND,
        'create_disposition': beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
    }
    
    if known_args.write_method == 'FILE_LOADS':
        write_kwargs['method'] = 'FILE_LOADS'
        write_kwargs['triggering_frequency'] = known_args.triggering_frequency
        write_kwargs['custom_gcs_temp_location'] = known_args.gcs_temp_location
    else:
        write_kwargs['method'] = 'STREAMING_INSERTS'
    
    with beam.Pipeline(options=pipeline_options) as p:
        (
            p
            | 'ReadFromPubSub' >> beam.io.ReadFromPubSub(subscription=known_args.input_subscription)
            | 'CleanAndAnonymize' >> beam.ParDo(CleanAndAnonymizeFn())
            | 'WriteToBigQuery' >> WriteToBigQuery(**write_kwargs)
        )

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    run()
