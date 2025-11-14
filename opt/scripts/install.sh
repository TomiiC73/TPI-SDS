#!/bin/bash
# Script de Instalación Inicial
# Banco Nacional

echo "Instalando dependencias..."

# Crear directorios del sistema
mkdir -p /var/log
mkdir -p /var/backup
mkdir -p /etc/config
mkdir -p /opt/scripts
mkdir -p /opt/scripts/.hidden  # Para scripts de desarrollo/testing
mkdir -p /home/admin
mkdir -p /srv

echo "Directorios creados"

# Copiar scripts de utilidad
# NOTA: Los scripts de pentesting están en /opt/scripts/.hidden
# TODO: Mover a ubicación más segura antes de producción

echo "Instalación completada"
