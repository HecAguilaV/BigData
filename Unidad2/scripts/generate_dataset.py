import csv
import json
import random
import os
from datetime import datetime, timedelta

def generate_rut():
    run = random.randint(5000000, 25000000)
    # Calulo digito verificador
    s = 0
    m = 2
    for d in reversed(str(run)):
        s += int(d) * m
        m = 9 if m == 7 else m + 1
    r = 11 - (s % 11)
    if r == 11:
        dv = '0'
    elif r == 10:
        dv = 'K'
    else:
        dv = str(r)
    return f"{run}-{dv}"

def generate_datasets():
    print("Iniciando la generación de datos de prueba para Grupo Cordillera...")
    os.makedirs("data", exist_ok=True)
    
    start_date = datetime(2016, 1, 1)
    end_date = datetime(2026, 5, 31)
    delta_days = (end_date - start_date).days
    
    nombres = ["Juan", "María", "Pedro", "Ana", "Carlos", "Sofía", "Diego", "Laura", "Luis", "Carmen", "Andrés", "Valentina", "José", "Francisca", "Javier", "Camila"]
    apellidos = ["Pérez", "González", "Muñoz", "Rojas", "Díaz", "Silva", "Contreras", "Espinoza", "Flores", "Valenzuela", "Castillo", "Tapia", "Reyes", "Morales", "Ortiz", "Gutiérrez"]
    metodos_pago = ["efectivo", "tarjeta_debito", "tarjeta_credito", "transferencia"]
    skus = [f"PROD-{i:03d}" for i in range(1, 101)]
    productos_precios = {sku: random.randint(1500, 990000) for sku in skus}
    
    # Generar un set fijo de clientes
    clientes = []
    for _ in range(50000):
        rut = generate_rut()
        nombre = f"{random.choice(nombres)} {random.choice(apellidos)}"
        clientes.append((rut, nombre))
    
    # 1. Generar ventas_historicas.csv
    csv_file = "data/ventas_historicas.csv"
    print(f"Generando {csv_file} (1,200,000 registros)...")
    
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id_transaccion", "fecha", "id_sucursal", "rut_cliente", "nombre_cliente", "sku", "cantidad", "monto_clp", "metodo_pago"])
        
        for i in range(1, 1200001):
            tx_id = f"TX-{i:010d}"
            # Fechas distribuidas aleatoriamente en el rango de 10 años
            random_days = random.randint(0, delta_days)
            fecha = (start_date + timedelta(days=random_days, hours=random.randint(8, 21), minutes=random.randint(0, 59))).strftime("%Y-%m-%d %H:%M:%S")
            id_sucursal = random.randint(1, 30)
            
            # 80% de compras son de clientes registrados, 20% cliente anónimo
            if random.random() < 0.8:
                rut_cliente, nombre_cliente = random.choice(clientes)
            else:
                rut_cliente, nombre_cliente = "", "CLIENTE ANONIMO"
                
            sku = random.choice(skus)
            cantidad = random.randint(1, 5)
            # Aplicar formato de moneda sucio a veces para que Dataprep limpie
            precio_unitario = productos_precios[sku]
            monto_clp = precio_unitario * cantidad
            
            # Introducir pequeñas anomalías de formato en 1% de los datos para limpiar en Dataprep
            if random.random() < 0.01:
                # Moneda sucia
                monto_clp_str = f"${monto_clp:,.0f}"
            else:
                monto_clp_str = str(monto_clp)
                
            metodo_pago = random.choice(metodos_pago)
            
            writer.writerow([tx_id, fecha, id_sucursal, rut_cliente, nombre_cliente, sku, cantidad, monto_clp_str, metodo_pago])
            
            if i % 200000 == 0:
                print(f"  -> {i} ventas generadas...")
                
    # 2. Generar sesiones_web.json (NDJSON)
    json_file = "data/sesiones_web.json"
    print(f"Generando {json_file} (300,000 registros)...")
    
    event_types = ["view_product", "add_to_cart", "purchase"]
    devices = ["mobile", "desktop", "tablet"]
    
    with open(json_file, "w", encoding="utf-8") as f:
        for i in range(1, 300001):
            session_id = f"SES-{i:010d}"
            # Fechas sesion concentradas en los ultimos 2 años
            random_days = random.randint(delta_days - 730, delta_days)
            dt = start_date + timedelta(days=random_days, hours=random.randint(0, 23), minutes=random.randint(0, 59))
            timestamp = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            ip_address = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
            
            # Cliente logueado o anonimo
            customer_id = random.choice(clientes)[0] if random.random() < 0.6 else None
            event_type = random.choices(event_types, weights=[0.7, 0.2, 0.1], k=1)[0]
            sku_product = random.choice(skus)
            device = random.choices(devices, weights=[0.6, 0.3, 0.1], k=1)[0]
            
            record = {
                "session_id": session_id,
                "timestamp": timestamp,
                "ip_address": ip_address,
                "customer_id": customer_id,
                "event_type": event_type,
                "sku_product": sku_product,
                "device": device
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            
            if i % 100000 == 0:
                print(f"  -> {i} sesiones generadas...")
                
    print("¡Generación completada de manera exitosa!")
    print(f"Ventas escritas en: {csv_file}")
    print(f"Sesiones escritas en: {json_file}")

if __name__ == "__main__":
    generate_datasets()
