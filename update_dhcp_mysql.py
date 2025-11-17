#!/usr/bin/env python3
import re
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# --- CONFIGURACIÓN DESDE VARIABLES DE ENTORNO ---
LEASE_FILE = os.getenv('LEASE_FILE', '/var/lib/dhcp/dhcpd.leases')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_NAME = os.getenv('DB_NAME', 'dhcp_leases_db')
DB_USER = os.getenv('DB_USER', 'dhcp_user')
DB_PASSWORD = os.getenv('DB_PASSWORD')

# Validar que la contraseña esté configurada
if not DB_PASSWORD:
    raise ValueError("La contraseña de la base de datos no está configurada. Por favor, establezca DB_PASSWORD en el archivo .env")
# ------------------------------------------------

def parse_lease_file(file_path):
    """
    Parsea el archivo dhcpd.leases y devuelve una lista de diccionarios
    con la información de los leases activos.
    """
    leases = []
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Expresión regular para encontrar cada bloque de lease
        lease_blocks = re.findall(r'lease\s+([\d\.]+)\s*\{([^}]+)\}', content, re.DOTALL)

        for ip, block_content in lease_blocks:
            lease_data = {'ip_address': ip}
            
            # Extraer información dentro del bloque
            # Hardware MAC
            mac_match = re.search(r'hardware\s+ethernet\s+([\da-fA-F:]+);', block_content)
            if mac_match:
                lease_data['mac_address'] = mac_match.group(1).lower()
            
            # Hostname
            hostname_match = re.search(r'client-hostname\s+"([^"]+)";', block_content)
            if hostname_match:
                lease_data['hostname'] = hostname_match.group(1)
            
            # Estado del lease
            state_match = re.search(r'binding\s+state\s+(\w+);', block_content)
            if state_match:
                lease_data['state'] = state_match.group(1)

            # Fechas de inicio y fin
            starts_match = re.search(r'starts\s+\d+\s+([\d/]+\s+[\d:]+);', block_content)
            ends_match = re.search(r'ends\s+\d+\s+([\d/]+\s+[\d:]+);', block_content)

            if starts_match and ends_match:
                # Formatear las fechas a un objeto datetime de Python
                lease_data['lease_start'] = datetime.strptime(starts_match.group(1), '%Y/%m/%d %H:%M:%S')
                lease_data['lease_end'] = datetime.strptime(ends_match.group(1), '%Y/%m/%d %H:%M:%S')

            # Solo nos interesan los leases activos
            if lease_data.get('state') == 'active':
                leases.append(lease_data)

    except FileNotFoundError:
        print(f"Error: No se encuentra el archivo de leases en {LEASE_FILE}")
        return None
    except Exception as e:
        print(f"Error al parsear el archivo de leases: {e}")
        return None
        
    return leases

def update_database(leases):
    """
    Conecta a la base de datos MySQL y actualiza la tabla de leases activos.
    La estrategia es limpiar la tabla y volver a insertar los datos activos.
    """
    if not leases:
        print("No hay leases activos para actualizar o ocurrió un error.")
        return

    connection = None
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )

        if connection.is_connected():
            cursor = connection.cursor()
            
            # Estrategia simple y efectiva: limpiar la tabla y volver a llenarla
            print("Limpiando la tabla 'active_leases'...")
            cursor.execute("DELETE FROM active_leases")
            
            print(f"Insertando {len(leases)} leases activos...")
            sql_insert_query = """
            INSERT INTO active_leases (ip_address, mac_address, hostname, lease_start, lease_end, state)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            # Preparar los datos para la inserción
            records_to_insert = [
                (
                    lease['ip_address'],
                    lease['mac_address'],
                    lease.get('hostname'), # Puede ser None
                    lease['lease_start'],
                    lease['lease_end'],
                    lease['state']
                ) for lease in leases
            ]
            
            cursor.executemany(sql_insert_query, records_to_insert)
            connection.commit()
            print(f"{cursor.rowcount} registros insertados correctamente en la tabla 'active_leases'.")

    except Error as e:
        print(f"Error al conectar o trabajar con la base de datos MySQL: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("Conexión a MySQL cerrada.")

if __name__ == '__main__':
    print("Iniciando sincronización de leases DHCP a MySQL...")
    active_leases = parse_lease_file(LEASE_FILE)
    if active_leases is not None:
        update_database(active_leases)
    print("Sincronización finalizada.")
