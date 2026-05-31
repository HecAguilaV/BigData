#!/bin/bash

# ==============================================================================
# Script de Ingesta de Datos: Grupo Cordillera (Evaluación Parcial N° 2)
# ==============================================================================

# Detener ejecucion si ocurre un error
set -e

# Configuración de variables (Personaliza estas variables)
PROJECT_ID=$(gcloud config get-value project 2>/dev/null || echo "grupo-cordillera-bigdata")
BUCKET_NAME="grupo-cordillera-datalake-${PROJECT_ID}"
REGION="us-central1"

echo "======================================================================"
echo "  Gentleman Guardian Angel - Ingesta de Datos para Grupo Cordillera"
echo "======================================================================"
echo "Proyecto GCP Activo: ${PROJECT_ID}"
echo "Bucket Destino: gs://${BUCKET_NAME}"
echo "======================================================================"

# 1. Verificar autenticación en Google Cloud
echo "1. Verificando autenticación de Google Cloud SDK..."
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "@"; then
    echo "⚠️  [ERROR] No se detectó ninguna cuenta de GCP activa."
    echo "Por favor ejecuta: 'gcloud auth login' antes de iniciar."
    exit 1
fi
echo "✅ Cuenta activa detectada."

# 2. Crear el Bucket en Cloud Storage si no existe
echo "2. Validando existencia del bucket de almacenamiento..."
if ! gcloud storage buckets describe gs://${BUCKET_NAME} &>/dev/null; then
    echo "Creando el bucket gs://${BUCKET_NAME} en la región ${REGION}..."
    gcloud storage buckets create gs://${BUCKET_NAME} --location=${REGION} --uniform-bucket-level-access
    echo "✅ Bucket creado exitosamente."
else
    echo "✅ El bucket gs://${BUCKET_NAME} ya existe."
fi

# 3. Subir los archivos locales al Bucket (Data Lake Raw Zone)
echo "3. Subiendo datos transaccionales de ventas (CSV)..."
if [ -f "data/ventas_historicas.csv" ]; then
    gcloud storage cp data/ventas_historicas.csv gs://${BUCKET_NAME}/raw/ventas_historicas.csv
    echo "✅ ventas_historicas.csv subido con éxito."
else
    echo "⚠️  [ERROR] No se encontró el archivo local 'data/ventas_historicas.csv'. Ejecuta primero 'python3 scripts/generate_dataset.py'."
    exit 1
fi

echo "4. Subiendo logs de navegación web (JSON)..."
if [ -f "data/sesiones_web.json" ]; then
    gcloud storage cp data/sesiones_web.json gs://${BUCKET_NAME}/raw/sesiones_web.json
    echo "✅ sesiones_web.json subido con éxito."
else
    echo "⚠️  [ERROR] No se encontró el archivo local 'data/sesiones_web.json'. Ejecuta primero 'python3 scripts/generate_dataset.py'."
    exit 1
fi

echo "======================================================================"
echo "✅ Proceso de Ingesta Completado Exitosamente."
echo "Los datos crudos están disponibles en la ruta gs://${BUCKET_NAME}/raw/"
echo "======================================================================"
