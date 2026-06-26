#!/bin/bash
set -e
cd "$(cd "$(dirname "$0")" && pwd)"
echo "=== Grupo Cordillera — Streamlit Dashboard ==="
echo "[0/2] Limpiando procesos anteriores..."
pkill -f "streamlit run" 2>/dev/null || true
pkill -f streaming_consumer 2>/dev/null || true
pkill -f streaming_producer 2>/dev/null || true
pkill -f aforo_consumer 2>/dev/null || true
pkill -f aforo_producer 2>/dev/null || true
rm -f data/streaming_consumer.pid data/streaming_producer.pid data/aforo_consumer.pid 2>/dev/null
sleep 2
echo "[1/2] Iniciando pipeline streaming web..."
source .venv/bin/activate
python Unidad3/scripts/run_simulation.py &
SIM_PID=$!
sleep 5
echo "[2/2] Iniciando Streamlit..."
streamlit run Unidad3/scripts/app.py --server.port 8501 --server.headless true &
ST_PID=$!
echo ""
echo "✅ Streamlit: http://localhost:8501"
echo "   PID simulación: $SIM_PID  |  PID streamlit: $ST_PID"
echo ""
echo "Presioná CTRL+C para detener todo."
trap "kill $SIM_PID $ST_PID 2>/dev/null; exit 0" SIGINT SIGTERM
wait
