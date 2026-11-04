"""Módulo de autenticación con Firebase Google Auth."""
import os
import uuid
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import firebase_admin
from firebase_admin import credentials, auth
import streamlit as st

from clases.ConfiguracionAuth import ConfiguracionAuth

try:
    from streamlit_google_auth import Authenticate
    GOOGLE_AUTH_AVAILABLE = True
except ImportError:
    GOOGLE_AUTH_AVAILABLE = False


class AutenticacionFirebase:
    """Gestiona la autenticación con Google usando Firebase."""

    def __init__(self):
        """Inicializa Firebase y carga configuración de Google Auth."""
        # Cargar configuración de auth
        self.config_auth = ConfiguracionAuth()
        
        # Obtener environment
        self.environment = os.getenv("ENVIRONMENT", "dev").lower()
        
        # Inicializar Firebase
        if not firebase_admin._apps:
            cred_path = Path(os.getenv("FIREBASE_KEY_PATH", "./etc/secrets/firebase_key.json"))
            if cred_path.exists():
                cred = credentials.Certificate(str(cred_path))
                firebase_admin.initialize_app(cred)

    @staticmethod
    def _procesar_callback_firebase() -> bool:
        """
        Procesa el callback de Firebase cuando redirige de vuelta a la app.
        Retorna True si se procesó exitosamente.
        """
        try:
            # Obtener parámetros de la URL
            query_params = st.query_params
            st.write(dict(query_params))
            # Verificar si hay un code de autorización
            if "code" in query_params or "authorization_code" in query_params:
                auth_code = query_params.get("code") or query_params.get("authorization_code")
                
                if auth_code:
                    #st.session_state.usuario_autenticado = True
                    st.session_state.usuario_id = auth_code
                    return True

            # Verificar si hay un token
            if "id_token" in query_params or "access_token" in query_params:
                id_token = query_params.get("id_token") or query_params.get("access_token")
                print(id_token)
                if id_token:
                    try:
                        # Decodificar el token de Firebase
                        decoded_token = auth.verify_id_token(id_token)
                        
                        # Extraer información del usuario
                        email = decoded_token.get("email", "")
                        nombre_completo = decoded_token.get("name", "Usuario")
                        nombres = nombre_completo.split(" ", 1)
                        
                        # Establecer sesión
                        st.session_state.usuario_autenticado = True
                        st.session_state.usuario_email = email
                        st.session_state.usuario_nombre = nombres[0]
                        st.session_state.usuario_apellido = nombres[1] if len(nombres) > 1 else ""
                        st.session_state.usuario_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, email))
                        
                        # Limpiar parámetros de URL
                        st.query_params.clear()
                        
                        return True
                    except Exception as e:
                        st.error(f"❌ Error al verificar token: {str(e)}")
                        return False
        
        except Exception as e:
            # Silent fail en callback
            print(e)
            pass
        
        return False

    @staticmethod
    def mostrar_modal_login() -> bool:
        """
        Muestra un modal de login con Google.
        Retorna True si el usuario está autenticado, False en caso contrario.
        """
        if "usuario_autenticado" not in st.session_state:
            st.session_state.usuario_autenticado = False
            st.session_state.usuario_email = None
            st.session_state.usuario_nombre = None
            st.session_state.usuario_apellido = None
            st.session_state.usuario_id = None

        # Si ya está autenticado, no mostrar modal
        #if st.session_state.usuario_autenticado:
        #    return True

        # Intentar procesar callback de Firebase
        if AutenticacionFirebase._procesar_callback_firebase():
            print("rerun")
        #    st.rerun()

        # Obtener configuración
        config = ConfiguracionAuth()
        client_id = config.obtener_client_id()
        environment = os.getenv("ENVIRONMENT", "dev").lower()
        es_desarrollo = environment == "dev"
        
        # Mostrar modal de login
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("# 🔐 RegHoras")
            st.markdown("### Inicia sesión con Google")

            # Intentar login real con streamlit-google-auth
            if GOOGLE_AUTH_AVAILABLE and client_id:
                try:
                    # Validar que la configuración esté completa
                    if not config.validar_configuracion():
                        st.error("❌ Configuración de Google Auth incompleta en secret-key.json")
                        st.stop()
                    
                    authenticator = Authenticate(
                        secret_credentials_path=ConfiguracionAuth.obtener_path_client_secret(),
                        cookie_key="reghoras_auth",
                        cookie_name="reghoras_auth",
                        cookie_expiry_days=30,
                        redirect_uri=os.getenv("REDIRECT_URI", "http://localhost:8501"),
                    )
                    
                    authenticator.login()

                    if st.session_state.get("authenticated", False):
                        user_info = st.session_state.user_info
                        st.write(dict(user_info))
                        st.session_state.usuario_autenticado = True
                        st.session_state.usuario_email = user_info.get("email", "")
                        
                        # Extraer nombre y apellido
                        nombre_completo = user_info.get("name", "Usuario")
                        nombres = nombre_completo.split(" ", 1)
                        st.session_state.usuario_nombre = nombres[0]
                        st.session_state.usuario_apellido = nombres[1] if len(nombres) > 1 else ""
                        
                        # Generar UUID único por email
                        st.session_state.usuario_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, st.session_state.usuario_email))
                        return True
                    return False
                        
                except Exception as e:
                    st.error(f"❌ Error en autenticación: {str(e)}")
            else:
                if not GOOGLE_AUTH_AVAILABLE:
                    st.warning("📦 streamlit-google-auth no está instalado")
                    st.info("Ejecuta: `pip install streamlit-google-auth`")
                if not client_id:
                    st.error("❌ No se pudo cargar Client ID desde secret-key.json")
                    st.info("Verifica que `STREAMLIT_AUTH_SECRET` esté correctamente configurado en `.env`")

            st.divider()

            # Opción de desarrollo: SOLO en ENVIRONMENT=dev
            if es_desarrollo:
                with st.expander("💻 Modo Desarrollo (Simular Login)", expanded=True):
                    st.caption("Solo disponible en ambiente de desarrollo")
                    email = st.text_input("Email de prueba", value="usuario@gmail.com", key="dev_email")
                    nombre = st.text_input("Nombre de prueba", value="Usuario", key="dev_nombre")
                    apellido = st.text_input("Apellido de prueba", value="Prueba", key="dev_apellido")

                    if st.button("✅ Simular Login", key="dev_login", use_container_width=True):
                        st.session_state.usuario_autenticado = True
                        st.session_state.usuario_email = email
                        st.session_state.usuario_nombre = nombre
                        st.session_state.usuario_apellido = apellido
                        st.session_state.usuario_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, email))
                        st.rerun()
            else:
                st.info("🔒 Ambiente de Producción - Solo Google OAuth disponible")

            # Info de configuración
            if client_id:
                st.success(f"✓ Autenticación configurada desde secret-key.json")
                st.caption(f"Project ID: {config.obtener_project_id()}")
                st.caption(f"Environment: {environment.upper()}")

        return False

    @staticmethod
    def obtener_usuario_actual():
        """Retorna la información del usuario actual."""
        return {
            "email": st.session_state.usuario_email,
            "nombre": st.session_state.usuario_nombre,
            "apellido": st.session_state.usuario_apellido,
            "id": st.session_state.usuario_id,
            "autenticado": st.session_state.usuario_autenticado,
        }

    @staticmethod
    def cerrar_sesion() -> None:
        """Cierra la sesión del usuario."""
        st.session_state.usuario_autenticado = False
        st.session_state.usuario_email = None
        st.session_state.usuario_nombre = None
        st.session_state.usuario_apellido = None
        st.session_state.usuario_id = None
        # Limpiar parámetros de URL si existen
        try:
            st.query_params.clear()
        except:
            pass
        st.rerun()

    @staticmethod
    def mostrar_usuario_en_sidebar() -> None:
        """Muestra el usuario autenticado en la barra lateral."""
        if st.session_state.usuario_autenticado:
            st.sidebar.markdown("---")
            nombre_completo = f"{st.session_state.usuario_nombre} {st.session_state.usuario_apellido}"
            st.sidebar.markdown(f"👤 **{nombre_completo}**")
            st.sidebar.caption(st.session_state.usuario_email)

            if st.sidebar.button("🚪 Cerrar sesión"):
                AutenticacionFirebase.cerrar_sesion()
