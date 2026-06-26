import os, sys, json, time, argparse, logging, threading
from datetime import datetime, timezone
from google.cloud import bigquery
from google.cloud import pubsub_v1
from google.cloud.bigquery import LoadJobConfig, WriteDisposition, CreateDisposition

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

buffer = []
buffer_lock = threading.Lock()
TABLE_ID = None

def get_client():
    return bigquery.Client(project="cordillerabi")

def ensure_table():
    global TABLE_ID
    BQ_CLIENT = get_client()
    schema = [
        bigquery.SchemaField("timestamp", "TIMESTAMP"),
        bigquery.SchemaField("id_sucursal", "INTEGER"),
        bigquery.SchemaField("nombre_sucursal", "STRING"),
        bigquery.SchemaField("lat", "FLOAT"),
        bigquery.SchemaField("lng", "FLOAT"),
        bigquery.SchemaField("capacidad_maxima", "INTEGER"),
        bigquery.SchemaField("aforo_actual", "INTEGER"),
        bigquery.SchemaField("personas_entran", "INTEGER"),
        bigquery.SchemaField("personas_salen", "INTEGER"),
        bigquery.SchemaField("porcentaje_ocupacion", "FLOAT"),
        bigquery.SchemaField("zona", "STRING"),
        bigquery.SchemaField("region", "STRING"),
    ]
    table = bigquery.Table(TABLE_ID, schema=schema)
    table.clustering_fields = ["id_sucursal"]
    table.time_partitioning = bigquery.TimePartitioning(
        field="timestamp",
        type_=bigquery.TimePartitioningType.DAY,
    )
    BQ_CLIENT.create_table(table, exists_ok=True)
    logging.info(f"Tabla asegurada: {TABLE_ID}")

def flush_buffer():
    global buffer
    with buffer_lock:
        if not buffer:
            return
        batch = buffer[:]
        buffer = []
    try:
        client = get_client()
        job_config = LoadJobConfig(
            write_disposition=WriteDisposition.WRITE_APPEND,
            create_disposition=CreateDisposition.CREATE_IF_NEEDED,
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        )
        job = client.load_table_from_json(batch, TABLE_ID, job_config=job_config)
        job.result()
        logging.info(f"Cargados {len(batch)} registros de aforo (Load Job)")
    except Exception as e:
        logging.error(f"Error en flush: {e}")
        with buffer_lock:
            buffer = batch + buffer

def callback(message):
    global buffer
    try:
        record = json.loads(message.data.decode("utf-8"))
        with buffer_lock:
            buffer.append(record)
        message.ack()
    except Exception as e:
        logging.warning(f"Mensaje inválido: {e}")
        message.nack()

def consume(project_id, subscription_id, output_table, batch_size=20, batch_interval=10):
    global TABLE_ID
    TABLE_ID = output_table
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(project_id, subscription_id)
    ensure_table()
    streaming_pull = subscriber.subscribe(subscription_path, callback=callback)
    logging.info(f"Consumiendo de {subscription_path}")
    
    def periodic_flush():
        while True:
            time.sleep(batch_interval)
            flush_buffer()
    
    t = threading.Thread(target=periodic_flush, daemon=True)
    t.start()
    
    try:
        streaming_pull.result()
    except KeyboardInterrupt:
        streaming_pull.cancel()
        flush_buffer()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--project_id", default="cordillerabi")
    parser.add_argument("--subscription_id", default="aforo-subscription")
    parser.add_argument("--output_table", default="cordillerabi.grupo_cordillera_dw.fact_aforo_streaming")
    parser.add_argument("--batch_size", type=int, default=20)
    parser.add_argument("--batch_interval", type=int, default=10)
    args = parser.parse_args()
    consume(args.project_id, args.subscription_id, args.output_table, args.batch_size, args.batch_interval)
