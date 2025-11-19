#!/bin/bash
# Script de Backup
# NO ES EL SCRIPT QUE BUSCAS

echo "Iniciando backup..."
tar -czf /var/backup/$(date +%Y%m%d).tar.gz /home
echo "Backup completado"
