#!/bin/bash
# ========================================
#   TPI-SDS - Script de Inicio Automático
# ========================================

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo "========================================"
echo "   Banco Nacional - TPI SDS"
echo "   Iniciando Sistema Completo"
echo "========================================"
echo ""

# Función para mostrar mensajes
info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Verificar que Docker esté instalado
if ! command -v docker &> /dev/null; then
    error "Docker no está instalado"
    echo ""
    echo "Por favor instala Docker desde:"
    echo "https://docs.docker.com/get-docker/"
    exit 1
fi

success "Docker detectado correctamente"
echo ""

# Verificar Docker Compose
if ! command -v docker-compose &> /dev/null; then
    error "Docker Compose no está instalado"
    echo ""
    echo "Por favor instala Docker Compose desde:"
    echo "https://docs.docker.com/compose/install/"
    exit 1
fi

success "Docker Compose detectado correctamente"
echo ""

# Detener contenedores previos si existen
info "Deteniendo contenedores previos (si existen)..."
docker-compose down 2>/dev/null || true

echo ""
info "Construyendo e iniciando contenedores..."
echo ""
echo "Este proceso puede tardar algunos minutos la primera vez."
echo "Por favor espera..."
echo ""

# Construir e iniciar
if docker-compose up -d --build; then
    echo ""
    echo "========================================"
    echo "   SISTEMA INICIADO CORRECTAMENTE"
    echo "========================================"
    echo ""
    echo "URLs de Acceso:"
    echo ""
    echo "  [+] Banco:      http://localhost:5000"
    echo "  [+] Enunciados: http://localhost:5001"
    echo "  [+] DB Admin:   http://localhost:8080"
    echo ""
    echo "========================================"
    echo "   CREDENCIALES"
    echo "========================================"
    echo ""
    echo "Login Bancario:"
    echo "  Usuario:  julian"
    echo "  Password: juli123"
    echo ""
    echo "OAuth FakeGoogle:"
    echo "  usuario@fakegoogle.com / fakegoogle123"
    echo "  admin@fakegoogle.com / admin123"
    echo "  hacker@fakegoogle.com / hacker123"
    echo ""
    echo "========================================"
    echo "   COMANDOS ÚTILES"
    echo "========================================"
    echo ""
    echo "Ver logs:        docker-compose logs -f"
    echo "Detener:         docker-compose down"
    echo "Reiniciar:       docker-compose restart"
    echo "Estado:          docker-compose ps"
    echo ""
    echo "========================================"
    echo ""
    
    # Abrir navegador (solo en sistemas con GUI)
    if command -v xdg-open &> /dev/null; then
        info "Abriendo navegador..."
        sleep 2
        xdg-open http://localhost:5000 &>/dev/null &
    elif command -v open &> /dev/null; then
        info "Abriendo navegador..."
        sleep 2
        open http://localhost:5000 &>/dev/null &
    fi
    
else
    echo ""
    error "Hubo un error al iniciar los contenedores"
    echo ""
    echo "Revisa los logs con: docker-compose logs"
    exit 1
fi
