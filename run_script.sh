#!/bin/bash

MAX_RETRIES=150
RETRY_DELAY=10
RETRY_COUNT=0
LOG_FILE="log_file.log"

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    python app.py
    EXIT_CODE=$?
    if [ $EXIT_CODE -eq 0 ]; then
        echo "$(date) - Script ejecutado exitosamente." | tee -a $LOG_FILE
        break
    else
        echo "$(date) - El script falló con código de salida $EXIT_CODE. Reiniciando en $RETRY_DELAY segundos..." | tee -a $LOG_FILE
        RETRY_COUNT=$((RETRY_COUNT+1))
        sleep $RETRY_DELAY
    fi
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "$(date) - Alcanzado el número máximo de reintentos. El script no se reiniciará más." | tee -a $LOG_FILE
fi
