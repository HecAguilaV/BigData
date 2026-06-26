import csv
import json
import os
import sys
import subprocess
from datetime import datetime

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
    csv_file = "data/ventas_historicas.csv"
    json_file = "data/ventas_clean.json"
    
    if not os.path.exists(csv_file):
        print(f"ERROR: No se encontró el archivo {csv_file}. Generá el dataset primero.")
        sys.exit(1)
        
    print(f"[+] Limpiando y estructurando {csv_file} localmente...")
    
    count = 0
    with open(csv_file, "r", encoding="utf-8") as f_in, open(json_file, "w", encoding="utf-8") as f_out:
        reader = csv.DictReader(f_in)
        
        for row in reader:
            tx_id = row["id_transaccion"]
            raw_fecha = row["fecha"]
            id_sucursal = int(row["id_sucursal"])
            rut = row["rut_cliente"]
            sku = row["sku"]
            cantidad = int(row["cantidad"])
            raw_monto = row["monto_clp"]
            
            # Realistic payment method distribution (no cash for e-commerce)
            h_val = sum(ord(c) for c in tx_id)
            if id_sucursal == 0:
                if h_val % 10 < 6:
                    metodo_pago = "tarjeta_debito"
                elif h_val % 10 < 9:
                    metodo_pago = "tarjeta_credito"
                else:
                    metodo_pago = "transferencia"
            else:
                if h_val % 10 < 4:
                    metodo_pago = "tarjeta_debito"
                elif h_val % 10 < 7:
                    metodo_pago = "efectivo"
                elif h_val % 10 < 9:
                    metodo_pago = "tarjeta_credito"
                else:
                    metodo_pago = "transferencia"
            
            # 1. Parsear fecha
            dt = datetime.strptime(raw_fecha, "%Y-%m-%d %H:%M:%S")
            fecha_iso = dt.strftime("%Y-%m-%dT%H:%M:%S")
            
            # 2. Extraer campos temporales
            dia_semana = dt.isoweekday() # Monday=1, Sunday=7
            mes = dt.month
            anio_iso = f"{dt.year}-01-01T00:00:00"
            
            # 3. Limpiar monto_clp
            monto_clean = raw_monto.replace("$", "").replace(",", "").replace(".", "").strip()
            try:
                monto_clp = int(monto_clean)
            except ValueError:
                monto_clp = 0
                
            # 4. Seudonimizar RUT
            id_anonimo = seudonimizar_rut(rut)
            
            # Armar registro JSON compatible con el esquema de BQ
            record = {
                "id_transaccion": tx_id,
                "fecha": fecha_iso,
                "dia_semana": dia_semana,
                "mes": mes,
                "anio": anio_iso,
                "id_sucursal": id_sucursal,
                "id_anonimo_cliente": id_anonimo,
                "sku": sku,
                "cantidad": cantidad,
                "monto_clp": monto_clp,
                "metodo_pago": metodo_pago
            }
            
            f_out.write(json.dumps(record) + "\n")
            count += 1
            if count % 200000 == 0:
                print(f"  -> {count} filas procesadas...")
                
    print(f"[✓] Limpieza completada. {count} registros escritos en {json_file}")
    
    # 5. Cargar directamente a BigQuery con bq load usando --replace (WRITE_TRUNCATE)
    print("[+] Cargando datos limpios directamente a BigQuery (Capa Batch)...")
    schema_str = "id_transaccion:STRING,fecha:DATETIME,dia_semana:INTEGER,mes:INTEGER,anio:DATETIME,id_sucursal:INTEGER,id_anonimo_cliente:STRING,sku:STRING,cantidad:INTEGER,monto_clp:INTEGER,metodo_pago:STRING"
    bq_cmd = [
        "bq", "load",
        "--source_format=NEWLINE_DELIMITED_JSON",
        "--replace",
        "grupo_cordillera_dw.fact_ventas",
        json_file,
        schema_str
    ]
    
    try:
        result = subprocess.run(bq_cmd, capture_output=True, text=True, check=True)
        print("[✓] Carga en BigQuery completada con éxito.")
        print(result.stdout)
        # Eliminar archivo temporal
        if os.path.exists(json_file):
            os.remove(json_file)
    except subprocess.CalledProcessError as e:
        print(f"[!] ERROR en la carga a BigQuery: {e.stderr}")
        sys.exit(1)

if __name__ == "__main__":
    main()
