import os
import sys
import json
import time
import argparse
import logging
from datetime import datetime
from google.cloud import pubsub_v1

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def check_pid(pid):
    """Check if a process with the given PID is running."""
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True

def publish_messages(project_id, topic_id, file_path, delay=0.5):
    """Publishes messages from a JSON file to a Pub/Sub topic."""
    
    # Check if file exists
    if not os.path.exists(file_path):
        logging.error(f"Error: The file {file_path} does not exist.")
        return

    # CONTROL DE EJECUCIÓN: PID file lock
    pid_file = "data/streaming_producer.pid"
    audit_log = "data/pipeline_execution.log"
    os.makedirs("data", exist_ok=True)
    
    if os.path.exists(pid_file):
        try:
            with open(pid_file, 'r') as pf:
                old_pid = int(pf.read().strip())
            if check_pid(old_pid):
                logging.error(f"BLOQUEADO: El productor ya está corriendo (PID: {old_pid}). Se aborta ejecución para evitar duplicidad de datos en Pub/Sub.")
                sys.exit(1)
        except ValueError:
            pass  # Invalid PID file, overwrite it

    current_pid = os.getpid()
    with open(pid_file, 'w') as pf:
        pf.write(str(current_pid))

    # REGISTRO DE ACTIVIDAD: Audit log
    with open(audit_log, 'a', encoding='utf-8') as al:
        al.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - INICIO - streaming_producer.py con PID {current_pid}\n")

    try:
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(project_id, topic_id)

        logging.info(f"Starting publisher to {topic_path}...")
        logging.info(f"Reading data from {file_path}")

        # Read and process the JSON file line by line (NDJSON format expected)
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_number, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue

                try:
                    # Validate JSON before sending
                    json_data = json.loads(line)
                    # Convert back to bytes for Pub/Sub
                    message_bytes = json.dumps(json_data).encode("utf-8")
                    
                    # Publish the message
                    future = publisher.publish(topic_path, message_bytes)
                    message_id = future.result()
                    
                    logging.info(f"Published message ID {message_id}: {line[:50]}...")
                    
                    # Pause to simulate real-time streaming
                    time.sleep(delay)
                    
                except json.JSONDecodeError as e:
                    logging.error(f"Invalid JSON at line {line_number}: {e}")
                except Exception as e:
                    logging.error(f"Error publishing message at line {line_number}: {e}")
    except Exception as e:
        logging.error(f"Error reading file: {e}")
    finally:
        # Cleanup PID file and log end of execution
        if os.path.exists(pid_file):
            os.remove(pid_file)
        with open(audit_log, 'a', encoding='utf-8') as al:
            al.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - FIN - streaming_producer.py finalizado\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulador de eventos Streaming hacia Pub/Sub")
    parser.add_argument("--project_id", type=str, default="cordillerabi", help="GCP Project ID")
    parser.add_argument("--topic_id", type=str, default="streaming-topic", help="Pub/Sub Topic ID")
    parser.add_argument("--file", type=str, default="data/sesiones_web.json", help="Ruta al archivo fuente")
    parser.add_argument("--delay", type=float, default=0.5, help="Segundos de demora entre envíos")
    
    args = parser.parse_args()
    publish_messages(args.project_id, args.topic_id, args.file, args.delay)
