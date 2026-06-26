import sys
import os
import argparse
import logging
import json
import re
import time
import threading
from datetime import datetime
from google.cloud import pubsub_v1
from google.cloud import bigquery

def check_pid(pid):
    """Check if a process with the given PID is running."""
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True

# Regex to find and replace the last octet of an IPv4 address
IP_MASK_REGEX = re.compile(r'\.\d+$')

def clean_and_anonymize(data):
    try:
        session_id = data.get('session_id')
        raw_timestamp = data.get('timestamp')
        ip_address = data.get('ip_address')
        customer_id = data.get('customer_id')
        event_type = data.get('event_type')
        sku_product = data.get('sku_product')
        device = data.get('device')
        
        # 1. Normalización del Timestamp (Formato BigQuery: YYYY-MM-DD HH:MM:SS)
        formatted_timestamp = None
        if raw_timestamp:
            try:
                clean_ts = raw_timestamp.replace('Z', '')
                dt = datetime.fromisoformat(clean_ts)
                formatted_timestamp = dt.strftime('%Y-%m-%d %H:%M:%S')
            except Exception as ts_err:
                logging.warning(f"Error parsing timestamp {raw_timestamp}: {ts_err}")
                formatted_timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        
        # 2. Seudonimización del ID de Cliente (customer_id / RUT)
        # Primeros 3 caracteres + 'XXXXXX-' + último caracter (Ley N° 21.719)
        id_anonimo_cliente = None
        if customer_id and str(customer_id).strip() != "":
            cust_str = str(customer_id).strip()
            if len(cust_str) >= 4:
                id_anonimo_cliente = f"{cust_str[:3]}XXXXXX-{cust_str[-1]}"
            else:
                id_anonimo_cliente = f"{cust_str}XXXXXX"
        
        # 3. Anonimización de IP a nivel de subred (Enmascarar último octeto)
        ip_anonima = None
        if ip_address:
            ip_anonima = IP_MASK_REGEX.sub('.0', ip_address)
        
        return {
            'session_id': session_id,
            'timestamp': formatted_timestamp,
            'ip_anonima': ip_anonima,
            'id_anonimo_cliente': id_anonimo_cliente,
            'event_type': event_type,
            'sku_product': sku_product,
            'device': device
        }
    except Exception as e:
        logging.error(f"Error processing record: {e}. Record: {data}")
        return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--project_id', required=True, help='GCP Project ID')
    parser.add_argument('--subscription_id', required=True, help='Pub/Sub Subscription ID')
    parser.add_argument('--output_table', required=True, help='Output BQ table, e.g. dataset.table')
    parser.add_argument('--batch_size', type=int, default=10, help='Number of records to batch before inserting')
    parser.add_argument('--batch_interval', type=int, default=10, help='Time interval in seconds to wait before flushing batch')
    
    args = parser.parse_args()

    # CONTROL DE EJECUCIÓN: PID file lock
    pid_file = "data/streaming_consumer.pid"
    audit_log = "data/pipeline_execution.log"
    os.makedirs("data", exist_ok=True)
    
    if os.path.exists(pid_file):
        try:
            with open(pid_file, 'r') as pf:
                old_pid = int(pf.read().strip())
            if check_pid(old_pid):
                logging.error(f"BLOQUEADO: El consumidor ya está corriendo (PID: {old_pid}). Se aborta ejecución para evitar duplicidad de datos en BigQuery.")
                sys.exit(1)
        except ValueError:
            pass  # Invalid PID file, overwrite it

    current_pid = os.getpid()
    with open(pid_file, 'w') as pf:
        pf.write(str(current_pid))

    # REGISTRO DE ACTIVIDAD: Audit log start
    with open(audit_log, 'a', encoding='utf-8') as al:
        al.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - INICIO - streaming_consumer.py con PID {current_pid}\n")
    
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(args.project_id, args.subscription_id)
    
    bq_client = bigquery.Client(project=args.project_id)
    dataset_id, table_id = args.output_table.split('.')
    table_ref = bq_client.dataset(dataset_id).table(table_id)
    
    logging.info(f"Listening for messages on {subscription_path}...")
    logging.info(f"Target BigQuery table: {args.output_table}")
    
    buffer = []
    buffer_lock = threading.Lock()
    last_flush_time = time.time()
    total_loaded_records = 0
    
    def flush_buffer():
        nonlocal last_flush_time, total_loaded_records
        batch_data = []
        with buffer_lock:
            if not buffer:
                return
            batch_data = list(buffer)
            buffer.clear()
        
        logging.info(f"Flushing {len(batch_data)} records to BigQuery...")
        try:
            job_config = bigquery.LoadJobConfig(
                write_disposition="WRITE_APPEND",
                source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
            )
            # Load the batch data as a job directly using load_table_from_json
            job = bq_client.load_table_from_json(batch_data, table_ref, job_config=job_config)
            job.result()  # Wait for the load job to complete
            logging.info(f"Successfully loaded {len(batch_data)} records to {args.output_table}")
            total_loaded_records += len(batch_data)
        except Exception as e:
            logging.error(f"Failed to load records to BigQuery: {e}")
        
        last_flush_time = time.time()

    def callback(message):
        try:
            data = json.loads(message.data.decode('utf-8'))
            cleaned = clean_and_anonymize(data)
            if cleaned:
                with buffer_lock:
                    buffer.append(cleaned)
            message.ack()
        except Exception as e:
            logging.error(f"Error handling message: {e}")
            message.nack()
            
    flow_control = pubsub_v1.types.FlowControl(max_messages=100)
    
    streaming_pull_future = subscriber.subscribe(
        subscription_path, callback=callback, flow_control=flow_control
    )
    
    try:
        while True:
            time.sleep(1)
            # Safe check of length with lock
            with buffer_lock:
                should_flush = len(buffer) >= args.batch_size or (time.time() - last_flush_time >= args.batch_interval and buffer)
            if should_flush:
                flush_buffer()
    except KeyboardInterrupt:
        flush_buffer()
        streaming_pull_future.cancel()
        logging.info("Consumer stopped.")
    finally:
        # Cleanup PID file and log end of execution
        if os.path.exists(pid_file):
            os.remove(pid_file)
        with open(audit_log, 'a', encoding='utf-8') as al:
            al.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - FIN - streaming_consumer.py finalizado. Total cargado: {total_loaded_records} filas\n")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    main()
