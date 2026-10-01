"""
Módulo para gestionar conexión y operaciones con Firebase Firestore.
Mantiene la misma interfaz que el gestor CSV para facilitar transición.
"""

from typing import List, Optional, Dict, Any
from datetime import date
import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st

from clases.Transaccion import Transaccion
from clases.firebase_config import FIRESTORE_CONFIG


class FirestoreManager:
    """Gestiona operaciones CRUD con Firebase Firestore."""

    def __init__(self, collection_name: str = None, credentials_path: str = None):
        """
        Inicializa el gestor de Firestore.
        
        Args:
            collection_name: Nombre de la colección en Firestore (default: "transacciones")
            credentials_path: Ruta al archivo JSON de credenciales
        """
        self.collection_name = collection_name or FIRESTORE_CONFIG["collection_name"]
        self.credentials_path = credentials_path or FIRESTORE_CONFIG.get("credentials_path", "firebase_key.json")
        self.db = None
        self._inicializar_firebase()

    def _inicializar_firebase(self) -> None:
        """Inicializa la conexión a Firebase usando la ruta correcta."""
        try:
            # Verificar si ya existe una app inicializada
            try:
                firebase_admin.get_app()
                print(f"[Firebase] App ya estaba inicializada")
            except ValueError:
                # App no inicializada, crear nueva
                print(f"[Firebase] Inicializando con: {self.credentials_path}")
                cred = credentials.Certificate(self.credentials_path)
                firebase_admin.initialize_app(cred)
                print(f"[Firebase] ✓ Inicializado exitosamente")
            
            self.db = firestore.client()
            print(f"[Firestore] ✓ Cliente de Firestore conectado")
            
        except FileNotFoundError as e:
            print(f"[Firebase] ✗ Archivo no encontrado: {self.credentials_path}")
            raise FileNotFoundError(f"Credenciales no encontradas en: {self.credentials_path}")
        except Exception as e:
            print(f"[Firebase] ✗ Error: {str(e)}")
            st.error(f"Error al conectar con Firebase: {str(e)}")
            raise

    def cargar_todas(self) -> List[Transaccion]:
        """
        Carga todas las transacciones desde Firestore.
        
        Returns:
            List[Transaccion]: Lista de transacciones
        """
        try:
            docs = self.db.collection(self.collection_name).stream()
            transacciones = []
            
            for doc in docs:
                data = doc.to_dict()
                data["id"] = doc.id  # Guardar el ID del documento
                transacciones.append(Transaccion.from_dict(data))
            
            return transacciones
        except Exception as e:
            st.warning(f"Error al cargar transacciones desde Firestore: {str(e)}")
            return []

    def guardar(self, transacciones: List[Transaccion]) -> bool:
        """
        Guarda o actualiza todas las transacciones en Firestore.
        
        Args:
            transacciones: Lista de transacciones a guardar
            
        Returns:
            bool: True si se guardó exitosamente
        """
        try:
            # Usar batch para optimizar múltiples escrituras
            batch = self.db.batch()
            collection_ref = self.db.collection(self.collection_name)
            
            # Limpiar documentos existentes (opcional, comentado por defecto)
            # docs = collection_ref.stream()
            # for doc in docs:
            #     batch.delete(doc.reference)
            
            # Agregar nuevos documentos
            for transaccion in transacciones:
                doc_ref = collection_ref.document(self._generar_doc_id(transaccion))
                batch.set(doc_ref, transaccion.to_dict(), merge=True)
            
            batch.commit()
            return True
        except Exception as e:
            st.error(f"Error al guardar en Firestore: {str(e)}")
            return False

    def agregar_una(self, transaccion: Transaccion) -> Optional[str]:
        """
        Agrega una única transacción a Firestore.
        
        Args:
            transaccion: Transacción a agregar
            
        Returns:
            str: ID del documento creado, None si falla
        """
        try:
            doc_ref = self.db.collection(self.collection_name).document()
            doc_ref.set(transaccion.to_dict())
            return doc_ref.id
        except Exception as e:
            st.error(f"Error al agregar transacción: {str(e)}")
            return None

    def actualizar_una(self, doc_id: str, transaccion: Transaccion) -> bool:
        """
        Actualiza una transacción existente.
        
        Args:
            doc_id: ID del documento
            transaccion: Datos actualizados
            
        Returns:
            bool: True si se actualizó exitosamente
        """
        try:
            self.db.collection(self.collection_name).document(doc_id).set(
                transaccion.to_dict(), merge=True
            )
            return True
        except Exception as e:
            st.error(f"Error al actualizar transacción: {str(e)}")
            return False

    def eliminar_una(self, doc_id: str) -> bool:
        """
        Elimina una transacción.
        
        Args:
            doc_id: ID del documento a eliminar
            
        Returns:
            bool: True si se eliminó exitosamente
        """
        try:
            self.db.collection(self.collection_name).document(doc_id).delete()
            return True
        except Exception as e:
            st.error(f"Error al eliminar transacción: {str(e)}")
            return False

    def obtener_por_fecha(self, fecha: date) -> List[Transaccion]:
        """
        Obtiene todas las transacciones de una fecha específica.
        
        Args:
            fecha: Fecha a buscar
            
        Returns:
            List[Transaccion]: Transacciones de esa fecha
        """
        try:
            docs = (
                self.db.collection(self.collection_name)
                .where("fecha", "==", str(fecha))
                .stream()
            )
            return [Transaccion.from_dict(doc.to_dict()) for doc in docs]
        except Exception as e:
            st.warning(f"Error al filtrar por fecha: {str(e)}")
            return []

    def buscar_por_descripcion(self, descripcion: str) -> List[Transaccion]:
        """
        Busca transacciones por descripción (búsqueda parcial).
        
        Args:
            descripcion: Texto a buscar
            
        Returns:
            List[Transaccion]: Transacciones que coinciden
        """
        try:
            docs = self.db.collection(self.collection_name).stream()
            resultados = [
                Transaccion.from_dict(doc.to_dict())
                for doc in docs
                if descripcion.lower() in doc.to_dict().get("descripcion", "").lower()
            ]
            return resultados
        except Exception as e:
            st.warning(f"Error en búsqueda: {str(e)}")
            return []

    def limpiar_coleccion(self) -> bool:
        """
        Elimina todos los documentos de la colección.
        ⚠️ USE CON CUIDADO
        
        Returns:
            bool: True si se limpió exitosamente
        """
        try:
            docs = self.db.collection(self.collection_name).stream()
            batch = self.db.batch()
            
            for doc in docs:
                batch.delete(doc.reference)
            
            batch.commit()
            return True
        except Exception as e:
            st.error(f"Error al limpiar colección: {str(e)}")
            return False

    @staticmethod
    def _generar_doc_id(transaccion: Transaccion) -> str:
        """
        Genera un ID único para un documento basado en la fecha y descripción.
        
        Args:
            transaccion: Transacción
            
        Returns:
            str: ID único
        """
        # Formato: fecha_primeras_palabras_de_descripcion
        fecha_str = str(transaccion.fecha).replace("-", "")
        desc = transaccion.descripcion.replace(" ", "_")[:20]
        return f"{fecha_str}_{desc}".lower()
