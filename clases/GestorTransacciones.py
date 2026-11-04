from __future__ import annotations

import os
from typing import List

import streamlit as st

from clases.Transaccion import Transaccion


class GestorTransacciones:
    """Gestiona las operaciones CRUD de transacciones usando Firestore."""

    ARCHIVO_DATOS = "transacciones.csv"
    ARCHIVO_USUARIOS = "usuarios.csv"

    USAR_FIRESTORE = os.getenv("USAR_FIRESTORE", "true").lower() == "true"

    def __init__(self, archivo: str = ARCHIVO_DATOS, usar_firestore: bool = None):
        """Inicializa el gestor de transacciones."""
        self.archivo = archivo
        self.archivo_usuarios = self.ARCHIVO_USUARIOS
        self.transacciones: List[Transaccion] = []
        self.usuarios: List[str] = []

        if usar_firestore is not None:
            self.usar_firestore = usar_firestore
        else:
            self.usar_firestore = self.USAR_FIRESTORE

        self.firestore_manager = None
        if self.usar_firestore:
            try:
                from clases.FirestoreManager import FirestoreManager

                self.firestore_manager = FirestoreManager()
            except Exception as error:
                self.usar_firestore = False
                st.error(f"No se pudo conectar con Firestore: {str(error)}")

    def cargar(self) -> None:
        """Carga transacciones y usuarios."""
        try:
            self.usuarios = self.firestore_manager.cargar_usuarios() if self.usar_firestore and self.firestore_manager else []
            if self.usar_firestore and self.firestore_manager:
                self.transacciones = self.firestore_manager.cargar_todas()
            else:
                self.transacciones = []
                self.usuarios = []
        except Exception as error:
            st.warning(f"Error al cargar transacciones: {str(error)}")

    def guardar(self) -> None:
        """Guarda transacciones y usuarios."""
        try:
            if self.usar_firestore and self.firestore_manager:
                self.firestore_manager.guardar(self.transacciones)
                self.firestore_manager.guardar_usuarios(self.usuarios)
        except Exception as error:
            st.error(f"Error al guardar: {str(error)}")

    def agregar(self, transaccion: Transaccion) -> None:
        """Agrega una nueva transacción a la lista local."""
        self.transacciones.append(transaccion)
        self.guardar()

    def agregar_usuario(self, nombre: str) -> bool:
        """Agrega un usuario si es válido y no está duplicado."""
        nombre_limpio = str(nombre).strip().upper()
        if not nombre_limpio:
            return False
        if nombre_limpio in self.usuarios:
            return False
        self.usuarios.append(nombre_limpio)
        self.usuarios.sort()
        if self.usar_firestore and self.firestore_manager:
            self.firestore_manager.guardar_usuarios(self.usuarios)
        return True

    def editar_usuario(self, nombre_actual: str, nombre_nuevo: str) -> bool:
        """Edita un usuario existente y actualiza transacciones asociadas."""
        nombre_actual_limpio = str(nombre_actual).strip().upper()
        nombre_nuevo_limpio = str(nombre_nuevo).strip().upper()
        if not nombre_actual_limpio or not nombre_nuevo_limpio:
            return False
        if nombre_actual_limpio not in self.usuarios:
            return False
        if nombre_actual_limpio == nombre_nuevo_limpio:
            return False
        if nombre_nuevo_limpio in self.usuarios:
            return False

        for transaccion in self.transacciones:
            if transaccion.usuario == nombre_actual_limpio:
                transaccion.usuario = nombre_nuevo_limpio

        self.usuarios = [nombre if nombre != nombre_actual_limpio else nombre_nuevo_limpio for nombre in self.usuarios]
        self.usuarios.sort()
        self.guardar()
        return True

    def eliminar_usuario(self, nombre: str) -> bool:
        """Elimina un usuario existente y limpia sus transacciones asociadas."""
        nombre_limpio = str(nombre).strip().upper()
        if not nombre_limpio or nombre_limpio not in self.usuarios:
            return False

        for transaccion in self.transacciones:
            if transaccion.usuario == nombre_limpio:
                transaccion.usuario = ""

        self.usuarios = [usuario for usuario in self.usuarios if usuario != nombre_limpio]
        self.guardar()
        return True

    def obtener_usuarios(self) -> List[str]:
        """Retorna la lista de usuarios disponibles."""
        return list(self.usuarios)

    def filtrar(
        self,
        usuario: str | None = None,
        fecha_desde: object | None = None,
        fecha_hasta: object | None = None,
    ) -> List[Transaccion]:
        """Filtra las transacciones por usuario y rango de fechas."""
        transacciones = list(self.transacciones)

        if usuario:
            transacciones = [
                t for t in transacciones if str(t.usuario).strip().upper() == str(usuario).strip().upper()
            ]

        if fecha_desde is not None:
            transacciones = [
                t for t in transacciones if t.fecha >= fecha_desde
            ]

        if fecha_hasta is not None:
            transacciones = [
                t for t in transacciones if t.fecha <= fecha_hasta
            ]

        return transacciones

    def eliminar(self, indice: int) -> None:
        """Elimina una transacción por su índice."""
        if 0 <= indice < len(self.transacciones):
            self.transacciones.pop(indice)
            self.guardar()

    def cambiar_backend(self, usar_firestore: bool) -> bool:
        """Cambia entre Firestore y modo sin almacenamiento persistente."""
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
            "backend": "Firestore" if self.usar_firestore else "Sin almacenamiento",
            "archivo": self.archivo if not self.usar_firestore else "transacciones (colección)",
        }
