# TODO LIST - Sistema Banco Nacional

## Pendientes de Seguridad
- [ ] Revisar vulnerabilidad RCE en transferencias
- [ ] Mover scripts de testing fuera de producción
- [ ] Los scripts están en /opt/scripts/.hidden - MOVER ANTES DE DEPLOY!
- [ ] Actualizar Flask a última versión
- [ ] Implementar rate limiting
- [ ] Añadir 2FA para admin

## Pendientes de Desarrollo  
- [ ] Mejorar UI del dashboard
- [ ] Añadir más productos bancarios
- [ ] Optimizar queries de base de datos

## Infraestructura
- [ ] Configurar backups automáticos
- [ ] Migrar a PostgreSQL
- [ ] Implementar logging centralizado

IMPORTANTE: El script de exploit RCE debe eliminarse antes de producción!
Ubicación actual: /opt/scripts/.hidden/rce_exploit.py
