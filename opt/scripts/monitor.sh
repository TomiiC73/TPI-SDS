#!/bin/bash
# Script de Monitoreo del Sistema
# Versión 1.0

echo "Verificando estado del sistema..."
df -h
free -m
uptime

echo "Script completado"
