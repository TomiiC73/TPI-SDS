# 🐳 Imagen oficial de Python 3.12 (Alpine para menor tamaño)
FROM python:3.12-slim

# Información del mantenedor
LABEL maintainer="TPI-SDS Team"
LABEL version="1.0"
LABEL description="Banco Nacional - Sistema de práctica de vulnerabilidades"

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    FLASK_APP=app_banco.py \
    FLASK_ENV=development

# Crear usuario no-root para seguridad (buena práctica)
RUN useradd -m -u 1000 bancouser && \
    mkdir -p /app && \
    chown -R bancouser:bancouser /app

# Establecer directorio de trabajo
WORKDIR /app

# Copiar requirements primero (aprovecha cache de Docker)
COPY requirements.txt .

# Instalar dependencias del sistema y Python
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        sqlite3 && \
    pip install --upgrade pip && \
    pip install -r requirements.txt && \
    apt-get remove -y gcc && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copiar el código de la aplicación
COPY --chown=bancouser:bancouser . .

# Asegurar que banco.db tenga permisos correctos
RUN if [ -f banco.db ]; then \
        chown bancouser:bancouser banco.db && \
        chmod 644 banco.db; \
    fi

# Cambiar al usuario no-root
USER bancouser

# Exponer el puerto 5000
EXPOSE 5000

# Healthcheck para verificar que la app esté funcionando
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/')" || exit 1

# Comando por defecto
CMD ["python", "app_banco.py"]
