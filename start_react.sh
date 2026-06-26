#!/bin/bash
set -e
cd "$(cd "$(dirname "$0")" && pwd)"
echo "=== Grupo Cordillera — React + FastAPI Dashboard ==="
echo "[0/3] Limpiando procesos anteriores..."
pkill -f "streamlit run" 2>/dev/null || true
pkill -f streaming_consumer 2>/dev/null || true
pkill -f streaming_producer 2>/dev/null || true
pkill -f aforo_consumer 2>/dev/null || true
pkill -f aforo_producer 2>/dev/null || true
pkill -f uvicorn 2>/dev/null || true
pkill -f "pnpm dev" 2>/dev/null || true
rm -f data/streaming_consumer.pid data/streaming_producer.pid 2>/dev/null
sleep 2
echo "[1/3] Iniciando pipeline streaming web + aforo..."
source .venv/bin/activate
python Unidad3/scripts/run_simulation.py &
SIM_PID=$!
sleep 5
echo "[2/3] Iniciando FastAPI backend..."
uvicorn Unidad3.api.main:app --port 8000 &
API_PID=$!
echo "[3/3] Iniciando React frontend..."
cd Unidad3/frontend
pnpm dev &
REACT_PID=$!
echo ""
echo "✅ React:  http://localhost:5173"
echo "✅ FastAPI: http://localhost:8000/api/health"
echo ""
echo "   PID simulación: $SIM_PID"
echo "   PID fastapi:    $API_PID"
echo "   PID react:      $REACT_PID"
echo ""
echo "Presioná CTRL+C para detener todo."
trap "kill $SIM_PID $API_PID $REACT_PID 2>/dev/null; exit 0" SIGINT SIGTERM
wait
