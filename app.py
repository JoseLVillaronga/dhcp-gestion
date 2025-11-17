#!/usr/bin/env python3
import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error
from flask import Flask, render_template, jsonify
from datetime import datetime
import json

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)

# Configuración de la base de datos
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'dhcp_leases_db'),
    'user': os.getenv('DB_USER', 'dhcp_user'),
    'password': os.getenv('DB_PASSWORD')
}

def get_active_leases():
    """
    Obtiene los leases activos más recientes por MAC address usando el query especificado.
    """
    leases = []
    connection = None
    
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            
            # Query proporcionado para obtener los leases más recientes por MAC
            query = """
            SELECT al.*
            FROM active_leases al
            JOIN (
                SELECT mac_address, MAX(id) AS id
                FROM active_leases
                GROUP BY mac_address
            ) t ON al.mac_address = t.mac_address AND al.id = t.id 
            ORDER BY ip_address
            """
            
            cursor.execute(query)
            leases = cursor.fetchall()
            
            # Formatear fechas para mejor visualización
            for lease in leases:
                if lease.get('lease_start'):
                    lease['lease_start'] = lease['lease_start'].strftime('%Y-%m-%d %H:%M:%S')
                if lease.get('lease_end'):
                    lease['lease_end'] = lease['lease_end'].strftime('%Y-%m-%d %H:%M:%S')
                
    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
        return []
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
    
    return leases

@app.route('/')
def dashboard():
    """
    Página principal del dashboard.
    """
    return render_template('dashboard.html')

@app.route('/api/leases')
def api_leases():
    """
    Endpoint API para obtener leases en formato JSON.
    """
    leases = get_active_leases()
    return jsonify({
        'success': True,
        'data': leases,
        'count': len(leases),
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

@app.route('/api/stats')
def api_stats():
    """
    Endpoint API para obtener estadísticas básicas.
    """
    leases = get_active_leases()
    
    # Calcular estadísticas
    total_leases = len(leases)
    unique_hosts = len(set(lease['hostname'] for lease in leases if lease.get('hostname')))
    leases_with_hostname = len([lease for lease in leases if lease.get('hostname')])
    
    return jsonify({
        'success': True,
        'stats': {
            'total_leases': total_leases,
            'unique_hosts': unique_hosts,
            'leases_with_hostname': leases_with_hostname,
            'leases_without_hostname': total_leases - leases_with_hostname
        }
    })

if __name__ == '__main__':
    print("Iniciando dashboard DHCP en puerto 5010...")
    print("Accede a: http://localhost:5010")
    app.run(host='0.0.0.0', port=5010, debug=False)
