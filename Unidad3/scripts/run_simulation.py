import subprocess
import time
import sys
import os
from datetime import datetime

def run_query(query):
    try:
        cmd = ["bq", "query", "--use_legacy_sql=false", "--format=csv", query]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        lines = result.stdout.strip().split('\n')
        if len(lines) > 1:
            return int(lines[1].strip())
    except Exception:
        return None
    return 0

def start_process(cmd, log_path, label):
    log = open(log_path, "w")
    proc = subprocess.Popen(cmd, stdout=log, stderr=log)
    time.sleep(2)
    if proc.poll() is not None:
        print(f"[!] ERROR: {label} falló al iniciar. Revisa {log_path}.")
        log.close()
        return None, log
    print(f"[✓] {label} iniciado (PID: {proc.pid})")
    return proc, log

def main():
    print("=" * 70)
    print("   SIMULADOR DE PIPELINE EN TIEMPO REAL - GRUPO CORDILLERA (EV3)")
    print("   Sesiones Web + Aforo IoT")
    print("=" * 70)

    for pid_f in ["data/streaming_consumer.pid", "data/streaming_producer.pid"]:
        if os.path.exists(pid_f):
            try:
                with open(pid_f) as pf:
                    pid = int(pf.read().strip())
                os.kill(pid, 0)
            except (OSError, ValueError):
                os.remove(pid_f)

    procs = []
    logs = []

    # 1. Consumer web
    print("\n[1/4] Iniciando Consumidor Web (Pub/Sub → BQ)...")
    p, l = start_process(
        [".venv/bin/python", "Unidad3/scripts/streaming_consumer.py",
         "--project_id", "cordillerabi", "--subscription_id", "streaming-subscription",
         "--output_table", "grupo_cordillera_dw.fact_sesiones_web_streaming",
         "--batch_size", "15", "--batch_interval", "5"],
        "data/consumer_stdout.log", "Consumidor Web"
    )
    if p is None: sys.exit(1)
    procs.append(p); logs.append(l)

    # 2. Producer web
    print("[2/4] Iniciando Productor Web (JSON → Pub/Sub)...")
    p, l = start_process(
        [".venv/bin/python", "Unidad3/scripts/streaming_producer.py",
         "--project_id", "cordillerabi", "--topic_id", "streaming-topic",
         "--file", "data/sesiones_web.json", "--delay", "1.0"],
        "data/producer_stdout.log", "Productor Web"
    )
    if p is None: sys.exit(1)
    procs.append(p); logs.append(l)

    # 3. Consumer aforo
    print("[3/4] Iniciando Consumidor Aforo IoT (Pub/Sub → BQ)...")
    p, l = start_process(
        [".venv/bin/python", "Unidad3/aforo/aforo_consumer.py",
         "--project_id", "cordillerabi", "--subscription_id", "aforo-subscription",
         "--output_table", "cordillerabi.grupo_cordillera_dw.fact_aforo_streaming",
         "--batch_size", "20", "--batch_interval", "10"],
        "data/consumer_aforo_stdout.log", "Consumidor Aforo"
    )
    if p is None: sys.exit(1)
    procs.append(p); logs.append(l)

    # 4. Producer aforo
    print("[4/4] Iniciando Productor Aforo IoT (sensor simulado → Pub/Sub)...")
    p, l = start_process(
        [".venv/bin/python", "Unidad3/aforo/aforo_producer.py",
         "--project_id", "cordillerabi", "--topic_id", "aforo-topic", "--delay", "5"],
        "data/producer_aforo_stdout.log", "Productor Aforo"
    )
    if p is None: sys.exit(1)
    procs.append(p); logs.append(l)

    print("\n" + "-" * 70)
    print(" Simulación en curso. Monitoreando BigQuery...")
    print(" Presioná CTRL+C para detener.")
    print("-" * 70)

    last_web = run_query("SELECT COUNT(*) FROM cordillerabi.grupo_cordillera_dw.fact_sesiones_web_streaming") or 0
    last_aforo = run_query("SELECT COUNT(*) FROM cordillerabi.grupo_cordillera_dw.fact_aforo_streaming") or 0
    print(f"[*] Web inicial: {last_web} | Aforo inicial: {last_aforo}")

    try:
        while True:
            time.sleep(5)
            for i, proc in enumerate(procs):
                if proc.poll() is not None:
                    print(f"[!] Un proceso se detuvo (índice {i})")
                    sys.exit(1)
            web = run_query("SELECT COUNT(*) FROM cordillerabi.grupo_cordillera_dw.fact_sesiones_web_streaming") or last_web
            aforo = run_query("SELECT COUNT(*) FROM cordillerabi.grupo_cordillera_dw.fact_aforo_streaming") or last_aforo
            now = datetime.now().strftime('%H:%M:%S')
            print(f"[{now}] Web: +{web - last_web} | Aforo: +{aforo - last_aforo}")
            last_web, last_aforo = web, aforo
    except KeyboardInterrupt:
        print("\n[+] Deteniendo simulación...")
    finally:
        for proc, log in zip(procs, logs):
            proc.terminate(); proc.wait(); log.close()
        print("[✓] Simulación finalizada.")

if __name__ == "__main__":
    main()
