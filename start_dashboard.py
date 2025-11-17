#!/usr/bin/env python3
"""
Script de inicio para el Dashboard DHCP
Gestión de Leases Activos
"""

import sys
import os
from dotenv import load_dotenv

def check_requirements():
    """Verificar que las dependencias estén instaladas"""
    required_modules = ['flask', 'mysql.connector', 'dotenv', 'gunicorn']
    missing_modules = []
    
    for module in required_modules:
        try:
            if module == 'dotenv':
                import dotenv
            elif module == 'flask':
                import flask
            elif module == 'mysql.connector':
                import mysql.connector
            elif module == 'gunicorn':
                import gunicorn
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print("❌ Faltan las siguientes dependencias:")
        for module in missing_modules:
            print(f"   - {module}")
        print("\n📦 Instala las dependencias con:")
        print("   pip install -r requirements.txt")
        return False
    
    return True

def check_env_file():
    """Verificar que el archivo .env exista"""
    if not os.path.exists('.env'):
        print("❌ No se encuentra el archivo .env")
        print("📝 Crea un archivo .env con la configuración de la base de datos:")
        print("   DB_HOST=localhost")
        print("   DB_NAME=dhcp_leases_db")
        print("   DB_USER=dhcp_user")
        print("   DB_PASSWORD=tu_contraseña")
        return False
    
    # Cargar y verificar variables críticas
    load_dotenv()
    
    if not os.getenv('DB_PASSWORD'):
        print("❌ La contraseña de la base de datos no está configurada en .env")
        return False
    
    return True

def start_with_gunicorn():
    """Iniciar con Gunicorn (producción)"""
    print("🚀 Iniciando con Gunicorn (modo producción)...")
    print("📱 Accede a: http://localhost:5010")
    print("⏹️  Presiona Ctrl+C para detener")
    print("=" * 40)
    
    import subprocess
    try:
        subprocess.run([
            'gunicorn',
            '--config', 'gunicorn.conf.py',
            'app:app'
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Servidor Gunicorn detenido por el usuario")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al iniciar Gunicorn: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ Gunicorn no encontrado. Instálalo con: pip install gunicorn")
        sys.exit(1)

def start_with_flask():
    """Iniciar con Flask development server"""
    print("🔧 Iniciando con Flask development server...")
    print("📱 Accede a: http://localhost:5010")
    print("⏹️  Presiona Ctrl+C para detener")
    print("=" * 40)
    
    try:
        from app import app
        app.run(host='0.0.0.0', port=5010, debug=False)
    except KeyboardInterrupt:
        print("\n🛑 Servidor Flask detenido por el usuario")
    except Exception as e:
        print(f"❌ Error al iniciar la aplicación: {e}")
        sys.exit(1)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Dashboard DHCP - Gestión de Leases Activos')
    parser.add_argument('--dev', action='store_true', 
                       help='Usar Flask development server (default: Gunicorn)')
    parser.add_argument('--port', type=int, default=5010,
                       help='Puerto del servidor (default: 5010)')
    
    args = parser.parse_args()
    
    print("🌐 Dashboard DHCP")
    print("=" * 40)
    
    # Verificar dependencias
    if not check_requirements():
        sys.exit(1)
    
    # Verificar configuración
    if not check_env_file():
        sys.exit(1)
    
    print("✅ Dependencias verificadas")
    print("✅ Configuración verificada")
    print()
    
    # Elegir servidor basado en argumentos
    if args.dev:
        start_with_flask()
    else:
        start_with_gunicorn()

if __name__ == '__main__':
    main()
