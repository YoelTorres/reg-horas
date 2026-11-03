from __future__ import annotations

from datetime import datetime, time
from typing import List

import pandas as pd
import streamlit as st
from streamlit_drawable_canvas import CanvasResult, st_canvas

from clases.GestorTransacciones import GestorTransacciones
from clases.PlanillaPDF import PlanillaPDF
from clases.Transaccion import Transaccion


class InterfazUI:
    """Interfaz de usuario de Streamlit."""

    LUGAR_TRABAJO = "La Reyna - Funes"
    HORAS_TRABAJO = 8
    meses = [
        "Enero",
        "Febrero",
        "Marzo",
        "Abril",
        "Mayo",
        "Junio",
        "Julio",
        "Agosto",
        "Septiembre",
        "Octubre",
        "Noviembre",
        "Diciembre",
    ]
    MES_ACTUAL = meses[datetime.now().month - 1]
    ANIO_ACTUAL = datetime.now().strftime("%Y")

    @staticmethod
    def mostrar_titulo() -> None:
        """Muestra el título de la aplicación."""
        st.title("Registros de horas")
        st.write("Lleva el control de tus horas de manera simple y visual")
        st.caption("Versión 1.0")

    @staticmethod
    def mostrar_formulario(gestor: GestorTransacciones) -> None:
        """Muestra formularios para usuarios y registros."""
        InterfazUI._mostrar_formulario_usuarios(gestor)
        InterfazUI._mostrar_formulario_transacciones(gestor)

    @staticmethod
    def _mostrar_formulario_usuarios(gestor: GestorTransacciones) -> None:
        """Shows the form to create users."""
        st.subheader("Usuarios", divider=True)
        with st.form("nuevo_usuario"):
            nombre_usuario = st.text_input("Nombre del usuario")
            enviado = st.form_submit_button("Agregar usuario")

            if enviado:
                if gestor.agregar_usuario(nombre_usuario):
                    st.success("Usuario agregado con éxito")
                    st.rerun()
                st.warning("Ingresa un nombre válido y que no esté repetido")

    @staticmethod
    def _mostrar_formulario_transacciones(gestor: GestorTransacciones) -> None:
        """Shows the form to create time records."""
        inicio_time = time(16, 0)
        salida_time = time(0, 0)
        usuarios = gestor.obtener_usuarios()

        st.subheader("Nuevo registro", divider=True)

        if not usuarios:
            st.info("Primero debes cargar al menos un usuario")
            return

        with st.form("nueva_transaccion"):
            usuario = st.selectbox("Usuario", options=usuarios)
            descripcion = str(
                st.text_input("Descripción del lugar", value=InterfazUI.LUGAR_TRABAJO)
            ).strip().upper()
            fecha = st.date_input("Fecha", format="DD/MM/YYYY")
            ingreso = st.time_input("Ingreso", value=inicio_time, step=300)
            salida = st.time_input("Salida", value=salida_time, step=300)
            enviado = st.form_submit_button("Enviar")

            if enviado:
                if not descripcion:
                    st.warning("La descripción del lugar es obligatoria")
                    return
                ingreso_str = ingreso.strftime("%H:%M")
                salida_str = salida.strftime("%H:%M")
                transaccion = Transaccion(descripcion, fecha, ingreso_str, salida_str, usuario=usuario)
                gestor.agregar(transaccion)
                st.success("Registro agregado con éxito")

    @staticmethod
    def mostrar_transacciones(
        transacciones: List[Transaccion], gestor: GestorTransacciones | None = None
    ) -> None:
        """Muestra tabla de transacciones con opciones de descarga y eliminación."""
        if transacciones:
            datos = [transaccion.to_dict() for transaccion in transacciones]
            df = pd.DataFrame(datos)
            st.dataframe(df)
            planilla_pdf = PlanillaPDF()
            nombre_usuario = transacciones[0].usuario if transacciones[0].usuario else "Sin usuario"
            pdf_doc = planilla_pdf.generar(
                nombre_usuario,
                InterfazUI.MES_ACTUAL,
                InterfazUI.ANIO_ACTUAL,
                df,
            )
            st.download_button(
                label="Exportar horas",
                data=pdf_doc,
                file_name="mis_horas.pdf",
                mime="application/octet-stream",
            )

            if gestor:
                st.subheader("Eliminar registro", divider=True)
                indices = list(range(len(transacciones)))
                descripciones = [
                    f"{t.usuario} - {t.descripcion} - {t.fecha} {t.ingreso}" for t in transacciones
                ]
                indice_seleccionado = st.selectbox(
                    "Selecciona un registro para eliminar",
                    indices,
                    format_func=lambda x: descripciones[x],
                    label_visibility="collapsed",
                )

                if st.button("🗑️ Eliminar", key="btn_eliminar"):
                    gestor.eliminar(indice_seleccionado)
                    st.success("Registro eliminado correctamente")
                    st.rerun()
        else:
            st.info("No hay transacciones registradas")

    @staticmethod
    def mostrar_firma() -> CanvasResult:
        """Muestra componente para dibujar firma."""
        st.subheader("✋ Firma")
        st.caption("Firmá dentro del recuadro utilizando el dedo, mouse o lapiz.")

        return st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)",
            stroke_width=5,
            stroke_color="black",
            background_color="#eee",
            update_streamlit=True,
            height=300,
            width=400,
            drawing_mode="freedraw",
            key="firma",
        )

    @staticmethod
    def firmar_multiples_registros(
        transacciones: List[Transaccion], gestor: GestorTransacciones
    ) -> None:
        """Permite firmar múltiples registros de transacciones."""
        if not transacciones:
            st.info("No hay transacciones para firmar")
            return

        if "indice_firma_actual" not in st.session_state:
            st.session_state.indice_firma_actual = 0

        indice_actual = st.session_state.indice_firma_actual

        if indice_actual < len(transacciones):
            transaccion_actual = transacciones[indice_actual]

            st.write(f"**Registro {indice_actual + 1} de {len(transacciones)}**")
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric("Usuario", transaccion_actual.usuario or "Sin usuario")
            with col2:
                st.metric("Fecha", str(transaccion_actual.fecha))
            with col3:
                st.metric("Lugar", transaccion_actual.descripcion)
            with col4:
                st.metric("Ingreso", str(transaccion_actual.ingreso))
            with col5:
                st.metric("Salida", str(transaccion_actual.salida))

            st.divider()
            st.write("### ✍️ Dibuja tu firma en el recuadro:")
            st.write("Usa el mouse, dedo o lápiz para firmar")
            st.write("")

            try:
                st_canvas(
                    fill_color="rgba(255, 165, 0, 0.3)",
                    stroke_width=5,
                    stroke_color="black",
                    background_color="#eee",
                    update_streamlit=True,
                    height=300,
                    width=600,
                    drawing_mode="freedraw",
                    key=f"firma_{indice_actual}",
                )
            except Exception as error:
                st.error(f"Error al cargar el canvas: {str(error)}")
        else:
            st.success("🎉 ¡Todos los registros han sido firmados!")
            if st.button("↻ Volver al inicio", key="reiniciar_firmas"):
                st.session_state.indice_firma_actual = 0
                st.rerun()
