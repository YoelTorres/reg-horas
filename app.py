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
    inicializar_sesion()
    InterfazUI.mostrar_titulo()

    with st.sidebar:
        InterfazUI.mostrar_formulario(gestor=st.session_state.gestor)
        #InterfazUI.mostrar_importador(gestor)
        #categorias_filtro, fecha_desde, fecha_hasta = InterfazUI.mostrar_filtros()

    transacciones_filtradas = st.session_state.gestor.filtrar()

    tab_resumen, tab_movimientos, tab_firmas, tab_analisis = st.tabs(["Resumen", "Movimientos", "Firmas", "Análisis"])

    #with tab_resumen:
    #    InterfazUI.mostrar_resumen(transacciones_filtradas)

    with tab_movimientos:
        InterfazUI.mostrar_transacciones(transacciones_filtradas, gestor=st.session_state.gestor)

    with tab_firmas:
        InterfazUI.firmar_multiples_registros(transacciones_filtradas, gestor=st.session_state.gestor)

    #with tab_analisis:
    #    InterfazUI.mostrar_analisis(transacciones_filtradas)

    st.session_state.gestor.guardar()


if __name__ == "__main__":
    main()






