from __future__ import annotations

import os
from typing import List

import pandas as pd
import streamlit as st

from clases.Transaccion import Transaccion


class GestorTransacciones:
    """
    Gestiona las operaciones CRUD de transacciones.
    Soporta tanto CSV como Firebase Firestore como backends.
    """

    ARCHIVO_DATOS = "transacciones.csv"
    ARCHIVO_USUARIOS = "usuarios.csv"

    USAR_FIRESTORE = os.getenv("USAR_FIRESTORE", "false").lower() == "true"

    def __init__(self, archivo: str = ARCHIVO_DATOS, usar_firestore: bool = None):
        """
        Inicializa el gestor de transacciones.

        Args:
            archivo: Ruta del archivo CSV (si no se usa Firestore)
            usar_firestore: Si True, usa Firestore. Si None, usa variable de entorno
        """
        self.archivo = archivo
        self.archivo_usuarios = self.ARCHIVO_USUARIOS
        self.transacciones: List[Transaccion] = []
        self.usuarios: List[str] = []

        if usar_firestore is not None:
            self.usar_firestore = usar_firestore
        else:
            self.usar_firestore = self.USAR_FIRESTORE

        backend_name = "🔥 Firestore" if self.usar_firestore else "📄 CSV"
        print(f"[GestorTransacciones] Backend: {backend_name} | USAR_FIRESTORE={self.USAR_FIRESTORE}")

        self.firestore_manager = None
        if self.usar_firestore:
            try:
                from clases.FirestoreManager import FirestoreManager

                self.firestore_manager = FirestoreManager()
                print("[GestorTransacciones] ✓ Firestore conectado exitosamente")
            except Exception as error:
                print(f"[GestorTransacciones] ✗ Error al conectar Firestore: {str(error)}")
                self.usar_firestore = False

    def cargar(self) -> None:
        """Carga transacciones y usuarios."""
        try:
            self._cargar_usuarios_csv()
            if self.usar_firestore and self.firestore_manager:
                self.transacciones = self.firestore_manager.cargar_todas()
                print(
                    "[GestorTransacciones] ✓ Cargadas "
                    f"{len(self.transacciones)} transacciones desde Firestore"
                )
            else:
                self._cargar_csv()
        except Exception as error:
            st.warning(f"Error al cargar transacciones: {str(error)}")

    def _cargar_csv(self) -> None:
        """Carga transacciones desde archivo CSV."""
        try:
            df = pd.read_csv(self.archivo)
            if not df.empty:
                self.transacciones = [Transaccion.from_dict(row.to_dict()) for _, row in df.iterrows()]
                print(
                    f"[GestorTransacciones] ✓ Cargadas {len(self.transacciones)} "
                    "transacciones desde CSV"
                )
        except FileNotFoundError:
            self.transacciones = []
        except Exception as error:
            st.warning(f"Error al cargar CSV: {str(error)}")

    def _cargar_usuarios_csv(self) -> None:
        """Carga usuarios desde archivo CSV."""
        try:
            df = pd.read_csv(self.archivo_usuarios)
            if "nombre" not in df.columns:
                self.usuarios = []
                return
            usuarios = [str(nombre).strip().upper() for nombre in df["nombre"].tolist() if str(nombre).strip()]
            self.usuarios = sorted(set(usuarios))
        except FileNotFoundError:
            self.usuarios = []
        except Exception as error:
            st.warning(f"Error al cargar usuarios: {str(error)}")
            self.usuarios = []

    def guardar(self) -> None:
        """Guarda transacciones y usuarios."""
        try:
            self._guardar_usuarios_csv()
            if self.usar_firestore and self.firestore_manager:
                self.firestore_manager.guardar(self.transacciones)
                print(
                    "[GestorTransacciones] ✓ Guardadas "
                    f"{len(self.transacciones)} transacciones en Firestore"
                )
            else:
                self._guardar_csv()
        except Exception as error:
            st.error(f"Error al guardar: {str(error)}")

    def _guardar_csv(self) -> None:
        """Guarda transacciones en archivo CSV."""
        datos = [transaccion.to_dict() for transaccion in self.transacciones]
        columnas = ["usuario", "descripcion", "fecha", "ingreso", "salida", "firma_id"]
        df = pd.DataFrame(datos, columns=columnas)
        df.to_csv(self.archivo, index=False)
        print(f"[GestorTransacciones] ✓ Guardadas {len(self.transacciones)} transacciones en CSV")

    def _guardar_usuarios_csv(self) -> None:
        """Guarda usuarios en archivo CSV."""
        df = pd.DataFrame({"nombre": self.usuarios})
        df.to_csv(self.archivo_usuarios, index=False)

    def agregar(self, transaccion: Transaccion) -> None:
        """Agrega una nueva transacción a la lista local."""
        self.transacciones.append(transaccion)

    def agregar_usuario(self, nombre: str) -> bool:
        """Add a user if the provided name is valid and not duplicated."""
        nombre_limpio = nombre.strip().upper()
        if not nombre_limpio:
            return False
        if nombre_limpio in self.usuarios:
            return False
        self.usuarios.append(nombre_limpio)
        self.usuarios.sort()
        self._guardar_usuarios_csv()
        return True

    def obtener_usuarios(self) -> List[str]:
        """Return the available users."""
        return list(self.usuarios)

    def filtrar(self) -> List[Transaccion]:
        """
        Filtra transacciones por categoría y rango de fechas.
        Actualmente retorna todas las transacciones.
        """
        return self.transacciones

    def eliminar(self, indice: int) -> None:
        """Elimina una transacción por su índice."""
        if 0 <= indice < len(self.transacciones):
            self.transacciones.pop(indice)
            if self.usar_firestore and self.firestore_manager:
                pass
            self.guardar()

    def cambiar_backend(self, usar_firestore: bool) -> bool:
        """
        Cambia entre CSV y Firestore.

        Args:
            usar_firestore: True para Firestore, False para CSV

        Returns:
            bool: True si el cambio fue exitoso
        """
        if usar_firestore and not self.firestore_manager:
            try:
                from clases.FirestoreManager import FirestoreManager

                self.firestore_manager = FirestoreManager()
                self.usar_firestore = True
                return True
            except Exception as error:
                st.error(f"Error al conectar con Firestore: {str(error)}")
                return False

        self.usar_firestore = usar_firestore
        return True

    def obtener_estadisticas(self) -> dict:
        """Retorna estadísticas de las transacciones."""
        return {
            "total": len(self.transacciones),
            "usuarios": len(self.usuarios),
            "backend": "Firestore" if self.usar_firestore else "CSV",
            "archivo": self.archivo if not self.usar_firestore else "transacciones (colección)",
        }
