#!/bin/bash

# Script de instalación del servicio systemd para Dashboard DHCP
# Se ejecuta como usuario actual con capacidades sudo

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir mensajes
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar que estamos en el directorio correcto
if [ ! -f "app.py" ] || [ ! -f "start_dashboard.py" ]; then
    print_error "No se encuentra app.py o start_dashboard.py. Ejecuta este script desde el directorio del proyecto."
    exit 1
fi

# Obtener información del usuario y entorno
CURRENT_USER=$(whoami)
USER_ID=$(id -u)
USER_GROUP=$(id -gn)
PROJECT_DIR=$(pwd)
PYTHON_PATH=$(which python3)

print_info "Instalando servicio systemd para Dashboard DHCP"
print_info "Usuario: $CURRENT_USER (ID: $USER_ID)"
print_info "Directorio del proyecto: $PROJECT_DIR"
print_info "Python: $PYTHON_PATH"

# Verificar que el usuario tenga sudo sin contraseña
if ! sudo -n true 2>/dev/null; then
    print_warning "El usuario requiere contraseña para sudo. Esto puede causar problemas en reinicios automáticos."
    read -p "¿Continuar de todos modos? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Instalación cancelada."
        exit 0
    fi
fi

# Crear archivo de servicio systemd para el usuario actual
SERVICE_FILE="/tmp/dhcp-dashboard-${CURRENT_USER}.service"

cat > "$SERVICE_FILE" << EOF
[Unit]
Description=DHCP Dashboard Web Service ($CURRENT_USER)
After=network.target mysql.service
Wants=mysql.service

[Service]
Type=exec
User=$CURRENT_USER
Group=$USER_GROUP
WorkingDirectory=$PROJECT_DIR
Environment=PATH=$PYTHON_PATH:$PROJECT_DIR/venv/bin:/usr/local/bin:/usr/bin:/bin
Environment=PYTHONPATH=$PROJECT_DIR
ExecStart=$PYTHON_PATH $PROJECT_DIR/start_dashboard.py
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=dhcp-dashboard-$CURRENT_USER

# Variables de entorno (si existen)
EnvironmentFile=-$PROJECT_DIR/.env

[Install]
WantedBy=multi-user.target
EOF

print_success "Archivo de servicio creado en $SERVICE_FILE"

# Copiar archivo de servicio a systemd
print_info "Copiando archivo de servicio a systemd..."
sudo cp "$SERVICE_FILE" "/etc/systemd/system/dhcp-dashboard-${CURRENT_USER}.service"

# Recargar systemd
print_info "Recargando systemd..."
sudo systemctl daemon-reload

# Habilitar y iniciar el servicio
print_info "Habilitando servicio dhcp-dashboard-${CURRENT_USER}..."
sudo systemctl enable "dhcp-dashboard-${CURRENT_USER}"

print_info "Iniciando servicio dhcp-dashboard-${CURRENT_USER}..."
sudo systemctl start "dhcp-dashboard-${CURRENT_USER}"

# Esperar un momento y verificar estado
sleep 2

print_info "Verificando estado del servicio..."
if sudo systemctl is-active --quiet "dhcp-dashboard-${CURRENT_USER}"; then
    print_success "✅ Servicio iniciado correctamente!"
else
    print_error "❌ Error al iniciar el servicio. Verifica los logs:"
    sudo systemctl status "dhcp-dashboard-${CURRENT_USER}" --no-pager
    exit 1
fi

# Mostrar información útil
echo
print_success "🎉 Instalación completada!"
echo
print_info "Comandos útiles:"
echo "  • Ver estado: sudo systemctl status dhcp-dashboard-${CURRENT_USER}"
echo "  • Ver logs: sudo journalctl -u dhcp-dashboard-${CURRENT_USER} -f"
echo "  • Reiniciar: sudo systemctl restart dhcp-dashboard-${CURRENT_USER}"
echo "  • Detener: sudo systemctl stop dhcp-dashboard-${CURRENT_USER}"
echo "  • Deshabilitar: sudo systemctl disable dhcp-dashboard-${CURRENT_USER}"
echo
print_info "El dashboard está accesible en:"
echo "  • http://localhost:5010"
echo "  • http://$(hostname -I | awk '{print $1}'):5010"
echo
print_warning "El servicio se iniciará automáticamente en cada reinicio del sistema."

# Limpiar archivo temporal
rm -f "$SERVICE_FILE"

print_success "¡Listo!"
