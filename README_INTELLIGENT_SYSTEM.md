# 🤖 Sistema de Scraping Inteligente SCJN

Sistema automatizado inteligente para descargar y gestionar tesis y jurisprudencia de la Suprema Corte de Justicia de la Nación (SCJN) con control de fases y optimización de recursos.

## 🎯 Características Principales

### 📊 Sistema de Fases Inteligente
- **Fase Inicial**: 3 horas diarias hasta completar el historial completo
- **Fase de Mantenimiento**: Lunes semanal para nuevas publicaciones
- **Transición Automática**: Cambio inteligente entre fases según progreso

### ⏰ Control de Tiempo Optimizado
- **Límite de tiempo por sesión**: Configurable (3 horas por defecto)
- **Límite de archivos por sesión**: 200 archivos máximo
- **Verificación de duplicados**: Evita descargas innecesarias
- **Recuperación automática**: Continúa donde se quedó

### 🔧 Configuración Flexible
- Horarios personalizables
- Límites ajustables
- Estimación de archivos totales
- Control de recursos del sistema

## 🚀 Instalación Rápida

### 1. Configuración Inicial
```bash
# Ejecutar configurador inteligente
python setup_intelligent_scraper.py
```

### 2. Opciones de Configuración
- **Configuración Rápida**: Valores optimizados por defecto
- **Configuración Personalizada**: Ajustar parámetros específicos

## 📋 Uso del Sistema

### Controlador Principal
```bash
# Iniciar controlador interactivo
python auto_scraper_controller.py
```

**Opciones del Controlador:**
1. 📊 Ver estado del sistema
2. 🚀 Iniciar fase inicial (3 horas diarias)
3. 🔧 Ejecutar mantenimiento semanal
4. ⚙️ Configurar parámetros
5. 📈 Ver estadísticas detalladas
6. 🔄 Ejecutar sesión manual
7. ⏰ Iniciar modo automático
8. 🛑 Detener sistema
9. 📋 Ver logs recientes

### Modo Daemon/Servicio
```bash
# Iniciar como servicio en segundo plano
python start_auto_scraper.py start

# Verificar estado
python start_auto_scraper.py status

# Detener servicio
python start_auto_scraper.py stop

# Reiniciar servicio
python start_auto_scraper.py restart
```

## ⚙️ Configuración del Sistema

### Parámetros Principales
```json
{
  "current_phase": "initial",
  "initial_phase_hours": 3,
  "initial_phase_start_time": "09:00",
  "maintenance_phase_start_time": "08:00",
  "max_files_per_session": 200,
  "total_estimated_files": 50000
}
```

### Archivos de Configuración
- `data/scraper_config.json`: Configuración del sistema
- `data/scraping_stats.json`: Estadísticas de descarga
- `logs/auto_scraper.log`: Logs del sistema
- `logs/daemon.log`: Logs del daemon

## 📊 Monitoreo y Estadísticas

### Estado del Sistema
- **Fase actual**: Inicial o Mantenimiento
- **Progreso**: Porcentaje completado
- **Archivos descargados**: Contador por fase
- **Duplicados encontrados**: Optimización
- **Errores**: Monitoreo de problemas

### Estadísticas Detalladas
- Descargas por sesión
- Descargas por día
- Transiciones de fase
- Rendimiento del sistema

## 🔄 Flujo de Trabajo

### Fase Inicial
1. **Descarga diaria**: 3 horas por día
2. **Términos amplios**: Búsqueda exhaustiva
3. **Control de duplicados**: Evita redundancia
4. **Límites de tiempo**: Respeta recursos
5. **Transición automática**: Al 95% de progreso

### Fase de Mantenimiento
1. **Ejecución semanal**: Lunes a las 8:00 AM
2. **Términos recientes**: Solo nuevas publicaciones
3. **Verificación de duplicados**: Mantiene integridad
4. **Actualización automática**: Registra fechas

## 🛠️ Personalización

### Ajustar Horarios
```python
# En el controlador
4. ⚙️ Configurar parámetros
   → 2. Hora de inicio diario
   → 3. Hora de mantenimiento semanal
```

### Modificar Límites
```python
# En el controlador
4. ⚙️ Configurar parámetros
   → 1. Horas diarias en fase inicial
   → 4. Archivos máximos por sesión
   → 5. Archivos estimados totales
```

### Sesiones Manuales
```python
# En el controlador
6. 🔄 Ejecutar sesión manual
   → 1. Fase inicial (con horas personalizadas)
   → 2. Fase de mantenimiento
```

## 📈 Optimización de Recursos

### Control de Memoria
- Cierre automático de drivers
- Limpieza de sesiones
- Gestión de archivos temporales

### Control de Red
- Pausas entre descargas
- Manejo de errores de conexión
- Reintentos automáticos

### Control de CPU
- Límites de tiempo por sesión
- Pausas entre operaciones
- Gestión de procesos

## 🔍 Solución de Problemas

### Logs del Sistema
```bash
# Ver logs recientes
tail -f logs/auto_scraper.log

# Ver logs del daemon
tail -f logs/daemon.log
```

### Verificar Estado
```bash
# Estado del daemon
python start_auto_scraper.py status

# Estado del sistema
python auto_scraper_controller.py
# → Opción 1: Ver estado del sistema
```

### Reiniciar Sistema
```bash
# Reiniciar daemon
python start_auto_scraper.py restart

# Reiniciar configuración
python setup_intelligent_scraper.py
# → Opción 4: Reiniciar configuración
```

## 📋 Requisitos del Sistema

### Dependencias
- Python 3.8+
- Selenium
- SQLAlchemy
- Schedule
- Requests
- BeautifulSoup4

### Recursos Recomendados
- **RAM**: 4GB mínimo, 8GB recomendado
- **Almacenamiento**: 10GB para base de datos
- **Conexión**: Internet estable
- **CPU**: 2 cores mínimo

## 🎯 Estrategia de Implementación

### Semana 1-2: Fase Inicial
- Descarga de 3 horas diarias
- Acumulación de historial
- Optimización de parámetros

### Semana 3+: Mantenimiento
- Verificación semanal
- Descarga de nuevas publicaciones
- Monitoreo continuo

### Evaluación Continua
- Revisión de estadísticas
- Ajuste de parámetros
- Optimización de rendimiento

## 🔐 Seguridad y Privacidad

### Protección de Datos
- No almacena información personal
- Solo contenido público de SCJN
- Logs locales sin datos sensibles

### Cumplimiento Legal
- Respeta robots.txt
- Pausas entre requests
- Uso responsable de recursos

## 📞 Soporte

### Documentación
- `GUIA_CONFIGURACION.md`: Guía detallada
- `README.md`: Documentación general
- Logs del sistema: Información de debug

### Comandos de Ayuda
```bash
# Ayuda del daemon
python start_auto_scraper.py help

# Ayuda del configurador
python setup_intelligent_scraper.py
```

---

**¡El sistema está listo para trabajar de manera inteligente y eficiente!** 🚀 