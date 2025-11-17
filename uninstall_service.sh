#!/bin/bash

# Script de desinstalación del servicio systemd para Dashboard DHCP

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

# Obtener usuario actual
CURRENT_USER=$(whoami)
SERVICE_NAME="dhcp-dashboard-${CURRENT_USER}"

print_info "Desinstalando servicio systemd: $SERVICE_NAME"

# Verificar si el servicio existe
if ! systemctl list-unit-files | grep -q "$SERVICE_NAME"; then
    print_warning "El servicio $SERVICE_NAME no existe. Nada que desinstalar."
    exit 0
fi

# Verificar si el usuario tiene sudo
if ! sudo -n true 2>/dev/null; then
    print_warning "Se requiere contraseña para sudo."
fi

# Preguntar confirmación
echo
print_warning "¿Estás seguro de que quieres desinstalar el servicio $SERVICE_NAME?"
print_warning "Esto detendrá y eliminará el servicio systemd."
read -p "¿Continuar? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_info "Desinstalación cancelada."
    exit 0
fi

# Detener el servicio si está corriendo
print_info "Deteniendo servicio $SERVICE_NAME..."
if sudo systemctl is-active --quiet "$SERVICE_NAME"; then
    sudo systemctl stop "$SERVICE_NAME"
    print_success "Servicio detenido."
else
    print_info "El servicio no estaba corriendo."
fi

# Deshabilitar el servicio
print_info "Deshabilitando servicio $SERVICE_NAME..."
if sudo systemctl is-enabled --quiet "$SERVICE_NAME"; then
    sudo systemctl disable "$SERVICE_NAME"
    print_success "Servicio deshabilitado."
else
    print_info "El servicio no estaba habilitado."
fi

# Eliminar archivo de servicio
print_info "Eliminando archivo de servicio..."
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
if [ -f "$SERVICE_FILE" ]; then
    sudo rm "$SERVICE_FILE"
    print_success "Archivo de servicio eliminado."
else
    print_warning "Archivo de servicio no encontrado."
fi

# Recargar systemd
print_info "Recargando systemd..."
sudo systemctl daemon-reload

# Limpiar residuos si existen
print_info "Limpiando residuos..."
sudo systemctl reset-failed "$SERVICE_NAME" 2>/dev/null || true

print_success "🎉 Desinstalación completada!"
echo
print_info "El servicio $SERVICE_NAME ha sido completamente eliminado."
print_warning "El dashboard ya no se iniciará automáticamente al reiniciar el sistema."
