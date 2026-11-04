"""
Módulo para gestionar conexión y operaciones con Firebase Firestore.
Mantiene la misma interfaz que el gestor CSV para facilitar transición.
"""

from datetime import date
from typing import List, Optional

import firebase_admin
import streamlit as st
from firebase_admin import credentials, firestore

from clases.Transaccion import Transaccion
from clases.firebase_config import FIRESTORE_CONFIG


class FirestoreManager:
    """Gestiona operaciones CRUD con Firebase Firestore."""

    def __init__(
        self,
        collection_name: str = None,
        credentials_path: str = None,
        users_collection_name: str = "usuarios",
    ):
        self.collection_name = collection_name or FIRESTORE_CONFIG["collection_name"]
        self.credentials_path = credentials_path or FIRESTORE_CONFIG.get("credentials_path")
        self.users_collection_name = users_collection_name
        self.db = None
        self._inicializar_firebase()

    def _inicializar_firebase(self) -> None:
        """Inicializa la conexión a Firebase usando la ruta correcta."""
        try:
            try:
                firebase_admin.get_app()
                print("[Firebase] App ya estaba inicializada")
            except ValueError:
                print(f"[Firebase] Inicializando con: {self.credentials_path}")
                cred = credentials.Certificate(self.credentials_path)
                firebase_admin.initialize_app(cred)
                print("[Firebase] ✓ Inicializado exitosamente")

            self.db = firestore.client()
            print("[Firestore] ✓ Cliente de Firestore conectado")

        except FileNotFoundError:
            print(f"[Firebase] ✗ Archivo no encontrado: {self.credentials_path}")
            raise FileNotFoundError(f"Credenciales no encontradas en: {self.credentials_path}")
        except Exception as error:
            print(f"[Firebase] ✗ Error: {str(error)}")
            st.error(f"Error al conectar con Firebase: {str(error)}")
            raise

    def cargar_todas(self) -> List[Transaccion]:
        """Carga todas las transacciones desde Firestore."""
        try:
            docs = self.db.collection(self.collection_name).stream()
            transacciones = []

            for doc in docs:
                data = doc.to_dict()
                data["id"] = doc.id
                transacciones.append(Transaccion.from_dict(data))

            return transacciones
        except Exception as error:
            st.warning(f"Error al cargar transacciones desde Firestore: {str(error)}")
            return []

    def cargar_usuarios(self) -> List[str]:
        """Carga la lista de usuarios desde Firestore."""
        try:
            docs = self.db.collection(self.users_collection_name).stream()
            usuarios = []
            for doc in docs:
                nombre = str(doc.to_dict().get("nombre", "")).strip().upper()
                if nombre:
                    usuarios.append(nombre)
            return sorted(set(usuarios))
        except Exception as error:
            st.warning(f"Error al cargar usuarios desde Firestore: {str(error)}")
            return []

    def guardar_usuarios(self, usuarios: List[str]) -> bool:
        """Guarda la lista de usuarios en Firestore y elimina los que ya no existen."""
        try:
            collection_ref = self.db.collection(self.users_collection_name)
            docs = list(collection_ref.stream())
            if docs:
                batch_delete = self.db.batch()
                for doc in docs:
                    batch_delete.delete(doc.reference)
                batch_delete.commit()

            batch = self.db.batch()
            for nombre in sorted(set(str(usuario).strip().upper() for usuario in usuarios if str(usuario).strip())):
                batch.set(collection_ref.document(nombre), {"nombre": nombre})
            batch.commit()
            return True
        except Exception as error:
            st.error(f"Error al guardar usuarios en Firestore: {str(error)}")
            return False

    def guardar(self, transacciones: List[Transaccion]) -> bool:
        """Guarda todas las transacciones en Firestore y elimina las que ya no existan."""
        try:
            collection_ref = self.db.collection(self.collection_name)
            docs = list(collection_ref.stream())

            if docs:
                batch_delete = self.db.batch()
                for doc in docs:
                    batch_delete.delete(doc.reference)
                batch_delete.commit()

            batch = self.db.batch()
            for transaccion in transacciones:
                doc_ref = collection_ref.document(self._generar_doc_id(transaccion))
                batch.set(doc_ref, transaccion.to_dict(), merge=True)

            batch.commit()
            return True
        except Exception as error:
            st.error(f"Error al guardar en Firestore: {str(error)}")
            return False

    def agregar_una(self, transaccion: Transaccion) -> Optional[str]:
        """Agrega una única transacción a Firestore."""
        try:
            doc_ref = self.db.collection(self.collection_name).document()
            doc_ref.set(transaccion.to_dict())
            return doc_ref.id
        except Exception as error:
            st.error(f"Error al agregar transacción: {str(error)}")
            return None

    def actualizar_una(self, doc_id: str, transaccion: Transaccion) -> bool:
        """Actualiza una transacción existente."""
        try:
            self.db.collection(self.collection_name).document(doc_id).set(
                transaccion.to_dict(), merge=True
            )
            return True
        except Exception as error:
            st.error(f"Error al actualizar transacción: {str(error)}")
            return False

    def eliminar_una(self, doc_id: str) -> bool:
        """Elimina una transacción."""
        try:
            self.db.collection(self.collection_name).document(doc_id).delete()
            return True
        except Exception as error:
            st.error(f"Error al eliminar transacción: {str(error)}")
            return False

    def obtener_por_fecha(self, fecha: date) -> List[Transaccion]:
        """Obtiene todas las transacciones de una fecha específica."""
        try:
            docs = self.db.collection(self.collection_name).where("fecha", "==", str(fecha)).stream()
            return [Transaccion.from_dict(doc.to_dict()) for doc in docs]
        except Exception as error:
            st.warning(f"Error al filtrar por fecha: {str(error)}")
            return []

    def buscar_por_descripcion(self, descripcion: str) -> List[Transaccion]:
        """Busca transacciones por descripción."""
        try:
            docs = self.db.collection(self.collection_name).stream()
            resultados = [
                Transaccion.from_dict(doc.to_dict())
                for doc in docs
                if descripcion.lower() in doc.to_dict().get("descripcion", "").lower()
            ]
            return resultados
        except Exception as error:
            st.warning(f"Error en búsqueda: {str(error)}")
            return []

    def limpiar_coleccion(self) -> bool:
        """Elimina todos los documentos de la colección."""
        try:
            docs = self.db.collection(self.collection_name).stream()
            batch = self.db.batch()

            for doc in docs:
                batch.delete(doc.reference)

            batch.commit()
            return True
        except Exception as error:
            st.error(f"Error al limpiar colección: {str(error)}")
            return False

    def eliminar_usuario(self, nombre: str) -> bool:
        """Elimina un usuario de Firestore."""
        try:
            self.db.collection(self.users_collection_name).document(str(nombre).strip().upper()).delete()
            return True
        except Exception as error:
            st.error(f"Error al eliminar usuario: {str(error)}")
            return False

    @staticmethod
    def _generar_doc_id(transaccion: Transaccion) -> str:
        """Genera un ID único para un documento basado en la fecha, usuario y descripción."""
        fecha_str = str(transaccion.fecha).replace("-", "")
        usuario = transaccion.usuario.replace(" ", "_")[:20] if transaccion.usuario else "sin_usuario"
        desc = transaccion.descripcion.replace(" ", "_")[:20]
        return f"{fecha_str}_{usuario}_{desc}".lower()
