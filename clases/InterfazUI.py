from __future__ import annotations

from calendar import monthrange
from datetime import date, datetime, time
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
        InterfazUI.mostrar_formulario_usuarios(gestor)
        InterfazUI.mostrar_formulario_transacciones(gestor)

    @staticmethod
    def mostrar_formulario_usuarios(gestor: GestorTransacciones) -> None:
        """Muestra el formulario de usuarios."""
        InterfazUI._mostrar_formulario_usuarios(gestor)

    @staticmethod
    def mostrar_formulario_transacciones(gestor: GestorTransacciones) -> None:
        """Muestra el formulario de alta de registros."""
        InterfazUI._mostrar_formulario_transacciones(gestor)

    @staticmethod
    def _mostrar_formulario_usuarios(gestor: GestorTransacciones) -> None:
        """Muestra formulario para crear, editar y eliminar usuarios."""
        st.subheader("Usuarios", divider=True)
        usuarios = gestor.obtener_usuarios()

        with st.form("nuevo_usuario"):
            nombre_usuario = st.text_input("Nombre del usuario")
            enviado = st.form_submit_button("Agregar usuario")

            if enviado:
                if gestor.agregar_usuario(nombre_usuario):
                    st.success("Usuario agregado con éxito")
                    st.rerun()
                else:
                    st.warning("Ingresa un nombre válido y que no esté repetido")

        if usuarios:
            col1, col2 = st.columns([4, 1])
            with col1:
                usuario_seleccionado = st.selectbox(
                    "Selecciona usuario",
                    options=usuarios,
                    key="usuario_editar_select",
                )
            with col2:
                st.write("")
                if st.button("🗑️ Eliminar", key="btn_eliminar_usuario"):
                    if gestor.eliminar_usuario(usuario_seleccionado):
                        st.success(f"Usuario {usuario_seleccionado} eliminado")
                        st.rerun()
                    else:
                        st.warning("No se pudo eliminar el usuario")

            st.write("")
            with st.form("editar_usuario"):
                nombre_editado = st.text_input(
                    "Nuevo nombre",
                    value=usuario_seleccionado,
                    key="usuario_editado_input",
                )
                if st.form_submit_button("Guardar cambios"):
                    if gestor.editar_usuario(usuario_seleccionado, nombre_editado):
                        st.success("Usuario actualizado con éxito")
                        st.rerun()
                    else:
                        st.warning("No se pudo actualizar el usuario")

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
        """Muestra tabla de transacciones con filtros y opciones de descarga y eliminación."""
        hoy = date.today()
        primer_dia = date(hoy.year, hoy.month, 1)
        ultimo_dia = date(hoy.year, hoy.month, monthrange(hoy.year, hoy.month)[1])

        usuarios = sorted({str(t.usuario).strip().upper() for t in transacciones if str(t.usuario).strip()})
        usuario_seleccionado = st.selectbox("Filtrar por usuario", ["Todos", *usuarios])
        fecha_desde = st.date_input("Desde", value=primer_dia, min_value=primer_dia, max_value=ultimo_dia)
        fecha_hasta = st.date_input("Hasta", value=ultimo_dia, min_value=primer_dia, max_value=ultimo_dia)

        if fecha_desde > fecha_hasta:
            st.warning("La fecha 'Desde' no puede ser mayor que 'Hasta'.")
            fecha_desde, fecha_hasta = fecha_hasta, fecha_desde

        transacciones_filtradas = gestor.filtrar(
            usuario=None if usuario_seleccionado == "Todos" else usuario_seleccionado,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
        ) if gestor else [
            t for t in transacciones if (fecha_desde <= t.fecha <= fecha_hasta) and (
                usuario_seleccionado == "Todos" or str(t.usuario).strip().upper() == usuario_seleccionado
            )
        ]

        if not transacciones_filtradas:
            st.info("No hay transacciones para los filtros seleccionados")
            return

        datos = [transaccion.to_dict() for transaccion in transacciones_filtradas]
        df = pd.DataFrame(datos)
        st.dataframe(df)

        planilla_pdf = PlanillaPDF()
        usuarios_en_tabla = sorted({str(t.usuario).strip().upper() for t in transacciones_filtradas if str(t.usuario).strip()})
        nombre_usuario = usuarios_en_tabla[0] if usuarios_en_tabla else "Sin usuario"
        pdf_doc = planilla_pdf.generar(
            nombre_usuario,
            InterfazUI.MES_ACTUAL,
            InterfazUI.ANIO_ACTUAL,
            df,
        )
        st.download_button(
            label="Exportar horas",
            data=pdf_doc,
            file_name=f"horas_{nombre_usuario.lower()}_{fecha_desde.isoformat()}_a_{fecha_hasta.isoformat()}.pdf",
            mime="application/octet-stream",
        )

        if gestor:
            st.subheader("Eliminar registro", divider=True)
            indices = list(range(len(transacciones_filtradas)))
            descripciones = [
                f"{t.usuario} - {t.descripcion} - {t.fecha} {t.ingreso}" for t in transacciones_filtradas
            ]
            indice_seleccionado = st.selectbox(
                "Selecciona un registro para eliminar",
                indices,
                format_func=lambda x: descripciones[x],
                label_visibility="collapsed",
            )

            if st.button("🗑️ Eliminar", key="btn_eliminar"):
                gestor.eliminar(
                    next(i for i, t in enumerate(transacciones) if t == transacciones_filtradas[indice_seleccionado])
                )
                st.success("Registro eliminado correctamente")
                st.rerun()

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
