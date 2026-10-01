from typing import List
from clases.Transaccion import Transaccion
import pandas as pd
import streamlit as st
import os


class GestorTransacciones:
    """
    Gestiona las operaciones CRUD de transacciones.
    Soporta tanto CSV como Firebase Firestore como backends.
    """

    ARCHIVO_DATOS = "transacciones.csv"
    
    # Determinar backend a usar por variable de entorno
    USAR_FIRESTORE = os.getenv("USAR_FIRESTORE", "false").lower() == "true"

    def __init__(self, archivo: str = ARCHIVO_DATOS, usar_firestore: bool = None):
        """
        Inicializa el gestor de transacciones.
        
        Args:
            archivo: Ruta del archivo CSV (si no se usa Firestore)
            usar_firestore: Si True, usa Firestore. Si None, usa variable de entorno
        """
        self.archivo = archivo
        self.transacciones: List[Transaccion] = []
        
        # Determinar qué backend usar
        if usar_firestore is not None:
            self.usar_firestore = usar_firestore
        else:
            self.usar_firestore = self.USAR_FIRESTORE
        
        # Debug: mostrar qué backend se está usando
        backend_name = "🔥 Firestore" if self.usar_firestore else "📄 CSV"
        print(f"[GestorTransacciones] Backend: {backend_name} | USAR_FIRESTORE={self.USAR_FIRESTORE}")
        
        # Inicializar backend de Firestore si está habilitado
        self.firestore_manager = None
        if self.usar_firestore:
            try:
                from clases.FirestoreManager import FirestoreManager
                self.firestore_manager = FirestoreManager()
                print(f"[GestorTransacciones] ✓ Firestore conectado exitosamente")
            except Exception as e:
                print(f"[GestorTransacciones] ✗ Error al conectar Firestore: {str(e)}")
                self.usar_firestore = False

    def cargar(self) -> None:
        """Carga transacciones desde Firestore o CSV."""
        try:
            if self.usar_firestore and self.firestore_manager:
                self.transacciones = self.firestore_manager.cargar_todas()
                print(f"[GestorTransacciones] ✓ Cargadas {len(self.transacciones)} transacciones desde Firestore")
            else:
                self._cargar_csv()
        except Exception as e:
            st.warning(f"Error al cargar transacciones: {str(e)}")

    def _cargar_csv(self) -> None:
        """Carga transacciones desde archivo CSV."""
        try:
            df = pd.read_csv(self.archivo)
            if not df.empty:
                self.transacciones = [Transaccion.from_dict(row.to_dict()) for _, row in df.iterrows()]
                print(f"[GestorTransacciones] ✓ Cargadas {len(self.transacciones)} transacciones desde CSV")
        except FileNotFoundError:
            pass
        except Exception as e:
            st.warning(f"Error al cargar CSV: {str(e)}")

    def guardar(self) -> None:
        """Guarda transacciones en Firestore o CSV."""
        try:
            if self.usar_firestore and self.firestore_manager:
                self.firestore_manager.guardar(self.transacciones)
                print(f"[GestorTransacciones] ✓ Guardadas {len(self.transacciones)} transacciones en Firestore")
            else:
                self._guardar_csv()
        except Exception as e:
            st.error(f"Error al guardar: {str(e)}")

    def _guardar_csv(self) -> None:
        """Guarda transacciones en archivo CSV."""
        if self.transacciones:
            datos = [t.to_dict() for t in self.transacciones]
            df = pd.DataFrame(datos)
            df.to_csv(self.archivo, index=False)
            print(f"[GestorTransacciones] ✓ Guardadas {len(self.transacciones)} transacciones en CSV")

    def agregar(self, transaccion: Transaccion) -> None:
        """Agrega una nueva transacción a la lista local."""
        self.transacciones.append(transaccion)

    def filtrar(self) -> List[Transaccion]:
        """
        Filtra transacciones por categoría y rango de fechas.
        Actualmente retorna todas las transacciones.
        """
        return self.transacciones

    def eliminar(self, indice: int) -> None:
        """Elimina una transacción por su índice."""
        if 0 <= indice < len(self.transacciones):
            transaccion = self.transacciones.pop(indice)
            if self.usar_firestore and self.firestore_manager:
                # Nota: para esto se necesaría almacenar el ID de Firestore
                # en el modelo de Transaccion
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
            except Exception as e:
                st.error(f"Error al conectar con Firestore: {str(e)}")
                return False
        else:
            self.usar_firestore = usar_firestore
            return True

    def obtener_estadisticas(self) -> dict:
        """
        Retorna estadísticas de las transacciones.
        
        Returns:
            dict: Estadísticas de transacciones
        """
        return {
            "total": len(self.transacciones),
            "backend": "Firestore" if self.usar_firestore else "CSV",
            "archivo": self.archivo if not self.usar_firestore else "transacciones (colección)"
        }