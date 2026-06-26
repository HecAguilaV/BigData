import json
import os
import sys
import re
import subprocess
from datetime import datetime

# Regex to find and replace the last octet of an IPv4 address
IP_MASK_REGEX = re.compile(r'\.\d+$')

def seudonimizar_rut(rut):
    if not rut or str(rut).strip() == "" or str(rut).strip() == "CLIENTE ANONIMO":
        return "CLIENTE ANONIMO"
    # Quitar puntos y espacios
    rut_str = str(rut).strip().replace(".", "").replace(" ", "")
    if "-" in rut_str:
        parts = rut_str.split("-")
        num = parts[0]
        dv = parts[1]
    else:
        num = rut_str[:-1]
        dv = rut_str[-1:]
    
    if len(num) >= 3:
        return f"{num[:3]}XXXXXX-{dv}"
    else:
        return f"{num}XXXXXX-{dv}"

def main():
    json_in_file = "data/sesiones_web.json"
    json_out_file = "data/sesiones_clean.json"
    
    if not os.path.exists(json_in_file):
        print(f"ERROR: No se encontró el archivo {json_in_file}. Generá el dataset primero.")
        sys.exit(1)
        
    print(f"[+] Limpiando y estructurando {json_in_file} localmente...")
    
    count = 0
    with open(json_in_file, "r", encoding="utf-8") as f_in, open(json_out_file, "w", encoding="utf-8") as f_out:
        for line in f_in:
            line = line.strip()
            if not line:
                continue
                
            try:
                data = json.loads(line)
                session_id = data.get('session_id')
                raw_timestamp = data.get('timestamp')
                ip_address = data.get('ip_address')
                customer_id = data.get('customer_id')
                event_type = data.get('event_type')
                sku_product = data.get('sku_product')
                device = data.get('device')
                
                # 1. Normalizar timestamp a formato BigQuery TIMESTAMP (ISO 8601 UTC)
                # Dataprep infiere TIMESTAMP, que acepta formato ISO YYYY-MM-DDTHH:MM:SSZ
                formatted_timestamp = None
                if raw_timestamp:
                    try:
                        clean_ts = raw_timestamp.replace('Z', '')
                        dt = datetime.fromisoformat(clean_ts)
                        formatted_timestamp = dt.strftime('%Y-%m-%d %H:%M:%S')
                    except Exception:
                        formatted_timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                
                # 2. Seudonimizar RUT
                id_anonimo = seudonimizar_rut(customer_id)
                
                # 3. Anonimizar IP
                ip_anonima = None
                if ip_address:
                    ip_anonima = IP_MASK_REGEX.sub('.0', ip_address)
                    
                # Armar registro JSON compatible con el esquema de BQ
                record = {
                    "session_id": session_id,
                    "timestamp": formatted_timestamp,
                    "ip_anonima": ip_anonima,
                    "id_anonimo_cliente": id_anonimo,
                    "event_type": event_type,
                    "sku_product": sku_product,
                    "device": device
                }
                
                f_out.write(json.dumps(record) + "\n")
                count += 1
                if count % 100000 == 0:
                    print(f"  -> {count} filas procesadas...")
            except Exception as e:
                print(f"Error procesando línea: {e}")
                
    print(f"[✓] Limpieza completada. {count} registros escritos en {json_out_file}")
    
    # 4. Cargar directamente a BigQuery con bq load usando --replace (WRITE_TRUNCATE)
    print("[+] Cargando datos limpios directamente a BigQuery (Capa Batch - Sesiones)...")
    bq_cmd = [
        "bq", "load",
        "--source_format=NEWLINE_DELIMITED_JSON",
        "--replace",
        "grupo_cordillera_dw.fact_sesiones_web_batch",
        json_out_file
    ]
    
    try:
        result = subprocess.run(bq_cmd, capture_output=True, text=True, check=True)
        print("[✓] Carga en BigQuery completada con éxito.")
        print(result.stdout)
        if os.path.exists(json_out_file):
            os.remove(json_out_file)
    except subprocess.CalledProcessError as e:
        print(f"[!] ERROR en la carga a BigQuery: {e.stderr}")
        sys.exit(1)

if __name__ == "__main__":
    main()
