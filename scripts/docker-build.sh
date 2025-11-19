#!/bin/bash
# Script para construir y ejecutar la aplicación con Docker

set -e

echo "🐳 ======================================"
echo "   Docker Builder - Banco Nacional"
echo "========================================="
echo ""

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para mostrar mensajes
info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Verificar que Docker esté instalado
if ! command -v docker &> /dev/null; then
    error "Docker no está instalado"
    echo "Instala Docker desde: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    error "Docker Compose no está instalado"
    echo "Instala Docker Compose desde: https://docs.docker.com/compose/install/"
    exit 1
fi

success "Docker y Docker Compose están instalados"
echo ""

# Menú de opciones
echo "Selecciona una opción:"
echo ""
echo "${GREEN}1.${NC} Construir imágenes Docker"
echo "${GREEN}2.${NC} Iniciar contenedores"
echo "${GREEN}3.${NC} Construir e iniciar (todo en uno)"
echo "${GREEN}4.${NC} Detener contenedores"
echo "${GREEN}5.${NC} Ver logs"
echo "${GREEN}6.${NC} Eliminar todo (contenedores + imágenes)"
echo "${GREEN}7.${NC} Reconstruir desde cero"
echo ""

read -p "Opción: " opcion

case $opcion in
    1)
        info "Construyendo imágenes Docker..."
        docker-compose build
        success "Imágenes construidas exitosamente"
        ;;
    2)
        info "Iniciando contenedores..."
        docker-compose up -d
        success "Contenedores iniciados"
        echo ""
        info "Acceso a la aplicación:"
        echo "  - Banco: http://localhost:5000"
        echo "  - Enunciados: http://localhost:5001"
        echo "  - DB Admin: http://localhost:8080"
        ;;
    3)
        info "Construyendo imágenes..."
        docker-compose build
        success "Imágenes construidas"
        echo ""
        info "Iniciando contenedores..."
        docker-compose up -d
        success "Contenedores iniciados"
        echo ""
        info "Acceso a la aplicación:"
        echo "  - Banco: http://localhost:5000"
        echo "  - Enunciados: http://localhost:5001"
        echo "  - DB Admin: http://localhost:8080"
        echo ""
        info "Ver logs en tiempo real:"
        echo "  docker-compose logs -f"
        ;;
    4)
        info "Deteniendo contenedores..."
        docker-compose down
        success "Contenedores detenidos"
        ;;
    5)
        info "Mostrando logs (Ctrl+C para salir)..."
        docker-compose logs -f
        ;;
    6)
        warning "Esto eliminará TODOS los contenedores e imágenes"
        read -p "¿Estás seguro? (s/N): " confirm
        if [[ $confirm == [sS] ]]; then
            info "Deteniendo contenedores..."
            docker-compose down
            info "Eliminando imágenes..."
            docker rmi banco-nacional:latest banco-enunciados:latest 2>/dev/null || true
            success "Todo eliminado"
        else
            warning "Operación cancelada"
        fi
        ;;
    7)
        info "Reconstruyendo desde cero (sin cache)..."
        docker-compose down
        docker-compose build --no-cache
        docker-compose up -d
        success "Aplicación reconstruida e iniciada"
        echo ""
        info "Acceso a la aplicación:"
        echo "  - Banco: http://localhost:5000"
        echo "  - Enunciados: http://localhost:5001"
        echo "  - DB Admin: http://localhost:8080"
        ;;
    *)
        error "Opción inválida"
        exit 1
        ;;
esac

echo ""
success "Operación completada"
