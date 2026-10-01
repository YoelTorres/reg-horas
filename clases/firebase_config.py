"""
Módulo de configuración de Firebase/Firestore.
Aquí se cargan las credenciales desde variables de entorno.
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Ruta donde se almacenará la clave de servicio JSON
FIREBASE_KEY_PATH = os.getenv("FIREBASE_KEY_PATH", "firebase-key.json")

# Configuración de la base de datos
FIRESTORE_CONFIG = {
    "project_id": os.getenv("FIREBASE_PROJECT_ID", ""),
    "database_id": os.getenv("FIREBASE_DATABASE_ID", "(default)"),
    "collection_name": os.getenv("FIREBASE_COLLECTION_NAME", "transacciones"),
    "credentials_path": FIREBASE_KEY_PATH,
}

def cargar_credenciales() -> dict:
    """
    Carga las credenciales de Firebase desde el archivo JSON.
    
    Returns:
        dict: Diccionario con las credenciales de Firebase
        
    Raises:
        FileNotFoundError: Si el archivo de credenciales no existe
        json.JSONDecodeError: Si el archivo no es JSON válido
    """
    if not Path(FIREBASE_KEY_PATH).exists():
        raise FileNotFoundError(
            f"Archivo de credenciales no encontrado: {FIREBASE_KEY_PATH}\n"
            f"Por favor, descarga tu clave de servicio desde Firebase Console "
            f"y colócala en: {FIREBASE_KEY_PATH}"
        )
    
    with open(FIREBASE_KEY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def validar_configuracion() -> bool:
    """
    Valida que la configuración de Firebase sea válida.
    
    Returns:
        bool: True si la configuración es válida
    """
    try:
        credenciales = cargar_credenciales()
        required_fields = ["type", "project_id", "private_key", "client_email"]
        return all(field in credenciales for field in required_fields)
    except Exception:
        return False
