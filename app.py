import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar .env ANTES de importar cualquier otra cosa
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path, verbose=True)

import streamlit as st
from clases.GestorTransacciones import GestorTransacciones
from clases.InterfazUI import InterfazUI


def inicializar_sesion() -> None:
    """Inicializa variables de sesión."""
    if "gestor" not in st.session_state:
        st.session_state.gestor = GestorTransacciones()
        st.session_state.gestor.cargar()


def main() -> None:
    """Función principal de la aplicación."""
    if not st.runtime.exists():
        print("Esta app debe ejecutarse con Streamlit: streamlit run app.py")
        return

    inicializar_sesion()
    InterfazUI.mostrar_titulo()

    with st.sidebar:
        InterfazUI.mostrar_formulario_transacciones(gestor=st.session_state.gestor)

    transacciones_filtradas = st.session_state.gestor.filtrar()

    tab_usuarios, tab_movimientos = st.tabs(["Usuarios", "Movimientos"])

    with tab_usuarios:
        InterfazUI.mostrar_formulario_usuarios(gestor=st.session_state.gestor)

    with tab_movimientos:
        InterfazUI.mostrar_transacciones(transacciones_filtradas, gestor=st.session_state.gestor)

    st.session_state.gestor.guardar()


if __name__ == "__main__":
    main()






