"""Módulo para cargar configuración de Google OAuth desde secret-key.json"""

import json
import os
from pathlib import Path
from typing import Dict, Optional


class ConfiguracionAuth:
    """Carga y gestiona la configuración de autenticación desde secret-key.json"""

    _instancia = None
    _config_cargada = False
    _datos_config = {}
    _ruta_secret = os.getenv("STREAMLIT_AUTH_SECRET", "./etc/secrets/secret-key.json")
    def __new__(cls):
        """Patrón Singleton para asegurar una sola instancia."""
        if cls._instancia is None:
            cls._instancia = super(ConfiguracionAuth, cls).__new__(cls)
        return cls._instancia

    def __init__(self):
        """Inicializa y carga la configuración si no está cargada."""
        if not ConfiguracionAuth._config_cargada:
            self._cargar_configuracion()
            ConfiguracionAuth._config_cargada = True

    @staticmethod
    def _cargar_configuracion() -> None:
        """Carga la configuración desde el archivo secret-key.json"""
        try:

            ConfiguracionAuth._ruta_secret = Path(ConfiguracionAuth._ruta_secret)

            if not ConfiguracionAuth._ruta_secret.exists():
                raise FileNotFoundError(f"Archivo no encontrado: {ConfiguracionAuth._ruta_secret}")

            with open(ConfiguracionAuth._ruta_secret, "r") as f:
                datos = json.load(f)
                # Acceder a la sección "web"
                ConfiguracionAuth._datos_config = datos.get("web", {})
                
                print(f"[ConfiguracionAuth] ✓ Configuración cargada desde {ConfiguracionAuth._ruta_secret}")

        except FileNotFoundError as e:
            print(f"[ConfiguracionAuth] ✗ {str(e)}")
            ConfiguracionAuth._datos_config = {}
        except json.JSONDecodeError as e:
            print(f"[ConfiguracionAuth] ✗ Error al parsear JSON: {str(e)}")
            ConfiguracionAuth._datos_config = {}

    @staticmethod
    def obtener_client_id() -> Optional[str]:
        """Retorna el Client ID de Google OAuth."""
        return ConfiguracionAuth._datos_config.get("client_id")

    @staticmethod
    def obtener_client_secret() -> Optional[str]:
        """Retorna el Client Secret de Google OAuth."""
        return ConfiguracionAuth._datos_config.get("client_secret")

    @staticmethod
    def obtener_project_id() -> Optional[str]:
        """Retorna el Project ID."""
        return ConfiguracionAuth._datos_config.get("project_id")

    @staticmethod
    def obtener_auth_uri() -> Optional[str]:
        """Retorna el URI de autenticación."""
        return ConfiguracionAuth._datos_config.get("auth_uri")

    @staticmethod
    def obtener_token_uri() -> Optional[str]:
        """Retorna el URI del token."""
        return ConfiguracionAuth._datos_config.get("token_uri")

    @staticmethod
    def obtener_redirect_uris() -> list:
        """Retorna los URIs de redirección autorizados."""
        return ConfiguracionAuth._datos_config.get("redirect_uris", [])

    @staticmethod
    def obtener_javascript_origins() -> list:
        """Retorna los orígenes JavaScript autorizados."""
        return ConfiguracionAuth._datos_config.get("javascript_origins", [])

    @staticmethod
    def obtener_toda_config() -> Dict:
        """Retorna toda la configuración."""
        return ConfiguracionAuth._datos_config.copy()

    @staticmethod
    def obtener_path_client_secret() -> str:
        """Retorna el path del client_secret de Google OAuth."""
        return ConfiguracionAuth._ruta_secret;

    @staticmethod
    def validar_configuracion() -> bool:
        """Valida que la configuración tenga los campos necesarios."""
        campos_requeridos = ["client_id", "client_secret", "project_id", "auth_uri", "token_uri"]
        config = ConfiguracionAuth.obtener_toda_config()
        
        campos_faltantes = [campo for campo in campos_requeridos if campo not in config]
        
        if campos_faltantes:
            print(f"[ConfiguracionAuth] ⚠️ Campos faltantes: {campos_faltantes}")
            return False
        
        return True
