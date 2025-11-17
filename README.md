# Dashboard DHCP - Gestión de Leases Activos

Sistema completo para gestión y monitoreo de leases DHCP con sincronización automática a MySQL y dashboard web en tiempo real.

## 🏗️ Arquitectura del Proyecto

```
dhcp-gestion/
├── .env                    # Configuración de credenciales (no versionado)
├── .gitignore             # Exclusiones de Git
├── requirements.txt       # Dependencias Python
├── README.md             # Este archivo
├── update_dhcp_mysql.py  # Script de sincronización DHCP → MySQL
├── app.py                # Aplicación web Flask (dashboard)
├── start_dashboard.py    # Script de inicio con verificaciones
└── templates/
    └── dashboard.html    # Interfaz web del dashboard
```

## 🚀 Funcionalidades

### Script de Sincronización (`update_dhcp_mysql.py`)
- ✅ Parsea archivo de leases DHCP (`/var/lib/dhcp/dhcpd.leases`)
- ✅ Filtra solo leases activos
- ✅ Sincroniza con base de datos MySQL
- ✅ Configuración segura mediante variables de entorno

### Dashboard Web (`app.py`)
- ✅ Interfaz moderna y responsiva
- ✅ Lista leases activos en tiempo real
- ✅ Estadísticas en vivo (total, hosts únicos, con/sin hostname)
- ✅ Auto-refresh cada 30 segundos
- ✅ API endpoints para datos JSON
- ✅ Diseño tipo dashboard (extensible)

## 📋 Requisitos

- Python 3.7+
- MySQL/MariaDB
- Acceso al archivo de leases DHCP
- Dependencias Python (ver `requirements.txt`)

## ⚙️ Configuración

### 1. Base de Datos
Crea la base de datos y tabla necesaria:

```sql
CREATE DATABASE dhcp_leases_db;
USE dhcp_leases_db;

CREATE TABLE active_leases (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ip_address VARCHAR(15) NOT NULL,
    mac_address VARCHAR(17) NOT NULL,
    hostname VARCHAR(255),
    lease_start DATETIME,
    lease_end DATETIME,
    state VARCHAR(20),
    INDEX idx_mac (mac_address),
    INDEX idx_ip (ip_address)
);
```

### 2. Configuración de Entorno
Copia y configura el archivo `.env`:

```bash
# Configuración de base de datos MySQL
DB_HOST=localhost
DB_NAME=dhcp_leases_db
DB_USER=dhcp_user
DB_PASSWORD=tu_contraseña_aqui

# Ruta del archivo de leases DHCP
LEASE_FILE=/var/lib/dhcp/dhcpd.leases
```

### 3. Instalación de Dependencias
```bash
pip install -r requirements.txt
```

## 🏃‍♂️ Uso

### Opción 1: Script de Inicio Recomendado (Gunicorn)
```bash
# Iniciar con Gunicorn (producción) - POR DEFECTO
python3 start_dashboard.py

# Iniciar con Flask development server (desarrollo)
python3 start_dashboard.py --dev

# Especificar puerto personalizado
python3 start_dashboard.py --port 8080
```

### Opción 2: Inicio Manual con Gunicorn
```bash
# Instalar dependencias
pip install -r requirements.txt

# Iniciar con Gunicorn (recomendado para producción)
gunicorn --config gunicorn.conf.py app:app

# O con parámetros directos
gunicorn --bind 0.0.0.0:5010 --workers 4 app:app
```

### Opción 3: Inicio Manual con Flask
```bash
# Sincronización manual de leases
python3 update_dhcp_mysql.py

# Iniciar dashboard con Flask development server
python3 app.py
```

### Opción 4: Servicio Systemd Automático (Recomendado)
```bash
# Instalar servicio para usuario actual (con sudo sin contraseña)
./install_service.sh

# Desinstalar servicio si es necesario
./uninstall_service.sh
```

**Características del servicio automático:**
- ✅ **Usuario Actual**: Se instala con el usuario que ejecuta el script
- ✅ **Directorio Actual**: Se ejecuta desde la carpeta del proyecto
- ✅ **Auto-reinicio**: Reinicio automático si falla
- ✅ **Startup Automático**: Inicia con el sistema
- ✅ **Logs Integrados**: Acceso via `journalctl`

### Opción 5: Servicio Systemd Manual (Avanzado)
```bash
# Copiar archivo de servicio (para usuario www-data)
sudo cp dhcp-dashboard.service /etc/systemd/system/

# Recargar systemd
sudo systemctl daemon-reload

# Iniciar y habilitar servicio
sudo systemctl start dhcp-dashboard
sudo systemctl enable dhcp-dashboard

# Verificar estado
sudo systemctl status dhcp-dashboard

# Ver logs
sudo journalctl -u dhcp-dashboard -f
```

### Opción 5: Automatización con Cron
Para sincronización automática cada 5 minutos:

```bash
# Editar crontab
crontab -e

# Agregar línea
*/5 * * * * /usr/bin/python3 /ruta/al/proyecto/update_dhcp_mysql.py
```

## 🌐 Acceso Web

Una vez iniciado el dashboard, accede a:
- **Dashboard Principal**: http://localhost:5010
- **API Leases**: http://localhost:5010/api/leases
- **API Estadísticas**: http://localhost:5010/api/stats

## 📊 API Endpoints

### GET `/api/leases`
Retorna todos los leases activos más recientes por MAC.

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "ip_address": "192.168.1.100",
      "mac_address": "aa:bb:cc:dd:ee:ff",
      "hostname": "laptop-usuario",
      "lease_start": "2025-01-17 10:30:00",
      "lease_end": "2025-01-17 12:30:00",
      "state": "active"
    }
  ],
  "count": 1,
  "timestamp": "2025-01-17 11:30:00"
}
```

### GET `/api/stats`
Retorna estadísticas básicas del sistema.

```json
{
  "success": true,
  "stats": {
    "total_leases": 25,
    "unique_hosts": 18,
    "leases_with_hostname": 20,
    "leases_without_hostname": 5
  }
}
```

## 🔍 Query Utilizado

El dashboard utiliza el siguiente query para obtener el lease más reciente por cada MAC address:

```sql
SELECT al.*
FROM active_leases al
JOIN (
    SELECT mac_address, MAX(id) AS id
    FROM active_leases
    GROUP BY mac_address
) t ON al.mac_address = t.mac_address AND al.id = t.id 
ORDER BY ip_address;
```

## 🎨 Características del Dashboard

- **Diseño Moderno**: Interfaz con gradientes y efectos glassmorphism
- **Responsivo**: Adaptado para móviles y tablets
- **Auto-refresh**: Actualización automática cada 30 segundos
- **Estadísticas en Vivo**: Métricas clave en tiempo real
- **Tabla Interactiva**: Hover effects y formato optimizado
- **Manejo de Errores**: Mensajes claros para problemas de conexión

## 🔒 Seguridad

- ✅ Credenciales en variables de entorno (.env)
- ✅ Archivo .env excluido del control de versiones
- ✅ Validación de configuración al inicio
- ✅ Sin autenticación (uso interno en red segura)

## 🚀 Extensiones Futuras

El dashboard está diseñado para ser fácilmente extensible:

- 📈 Gráficos y visualizaciones
- 🔍 Búsqueda y filtros avanzados
- 📊 Histórico de leases
- ⚠️ Alertas y notificaciones
- 🏢 Segmentación por VLAN/subred
- 👥 Múltiples usuarios con autenticación
- 📱 Aplicación móvil

## 🐛 Troubleshooting

### Problemas Comunes

**Error: "No se encuentra el archivo .env"**
```bash
# Asegúrate de estar en el directorio correcto
ls -la .env

# Crea el archivo si no existe
cp .env.example .env  # (si tuvieras una plantilla)
```

**Error de conexión a MySQL**
```bash
# Verifica credenciales en .env
# Asegúrate de que MySQL esté corriendo
# Verifica permisos del usuario de la base de datos
```

**Error: "No se encuentra el archivo de leases"**
```bash
# Verifica la ruta en .env
ls -la /var/lib/dhcp/dhcpd.leases

# Asegúrate de tener permisos de lectura
sudo chmod 644 /var/lib/dhcp/dhcpd.leases
```

## 📝 Licencia

Proyecto de uso interno para gestión de leases DHCP.
