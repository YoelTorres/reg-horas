import streamlit as st
from datetime import datetime, timedelta, time, date
import pandas as pd
from typing import List
from streamlit_drawable_canvas import st_canvas, CanvasResult

from clases.PlanillaPDF import PlanillaPDF
from clases.GestorTransacciones import GestorTransacciones
from clases.Transaccion import Transaccion
from clases.GestorFirmas import GestorFirmas


class InterfazUI:
    """Interfaz de usuario de Streamlit."""

    LUGAR_TRABAJO = "La Reyna - Funes"
    HORAS_TRABAJO = 8

    @staticmethod
    def mostrar_titulo() -> None:
        """Muestra el título de la aplicación."""
        st.title("Registros de horas")
        st.write("Lleva el control de tus horas de manera simple y visual")
        st.caption("Versión 1.0")

    @staticmethod
    def mostrar_formulario(gestor: GestorTransacciones) -> None:
        """Muestra formulario para agregar nueva transacción."""
        # Crear valores por defecto como objetos time (no strings)
        inicio_time = time(16, 0)  # 16:00 en formato 24hs
        salida_time = time(0, 0)   # 00:00 en formato 24hs

        with st.form("nueva_transaccion"):
            descripcion = str(st.text_input("Descripción del lugar",
                                            value=InterfazUI.LUGAR_TRABAJO)).upper()
            fecha = st.date_input("Fecha", format="DD/MM/YYYY")
            # Pasar objetos time(), no strings
            ingreso = st.time_input("Ingreso", value=inicio_time, step=300)  # step=300 segundos (5 min)
            salida = st.time_input("Salida", value=salida_time, step=300)
            enviado = st.form_submit_button("Enviar")

            if enviado:
                # Convertir time a string HH:MM para almacenar
                ingreso_str = ingreso.strftime("%H:%M")
                salida_str = salida.strftime("%H:%M")
                transaccion = Transaccion(descripcion, fecha, ingreso_str, salida_str)
                gestor.agregar(transaccion)
                st.success("Registro agregado con éxito")

    @staticmethod
    def mostrar_transacciones(transacciones: List[Transaccion], gestor: GestorTransacciones = None) -> None:
        """Muestra tabla de transacciones con opciones de descarga y eliminación."""
        if transacciones:
            datos = [t.to_dict() for t in transacciones]
            df = pd.DataFrame(datos)
            st.dataframe(df)
            #csv_buffer = df.to_csv(index=False)
            planillaPDF = PlanillaPDF()
            pdf_doc = planillaPDF.generar("Micaela Santa María", "Septiembre", 2026, df)
            st.download_button(
                label="Exportar horas",
                data=pdf_doc,
                file_name="mis_horas.pdf",
                mime="application/octet-stream",
            )

            if gestor:
                st.subheader("Eliminar registro", divider=True)
                indices = list(range(len(transacciones)))
                descripciones = [f"{t.descripcion} - {t.fecha} {t.ingreso}" for t in transacciones]
                indice_seleccionado = st.selectbox(
                    "Selecciona un registro para eliminar",
                    indices,
                    format_func=lambda x: descripciones[x],
                    label_visibility="collapsed"
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
                key=f"firma"
            )

    @staticmethod
    def firmar_multiples_registros(transacciones: List[Transaccion], gestor: GestorTransacciones) -> None:
        """Permite firmar múltiples registros de transacciones."""
        if not transacciones:
            st.info("No hay transacciones para firmar")
            return

        # Inicializar índice actual en session_state
        if "indice_firma_actual" not in st.session_state:
            st.session_state.indice_firma_actual = 0
        
        indice_actual = st.session_state.indice_firma_actual
        
        if indice_actual < len(transacciones):
            #print(indice_actual, len(transacciones))
            transaccion_actual = transacciones[indice_actual]
            
            # Mostrar información de la transacción actual
            st.write(f"**Registro {indice_actual + 1} de {len(transacciones)}**")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Fecha", str(transaccion_actual.fecha))
            with col2:
                st.metric("Lugar", transaccion_actual.descripcion)
            with col3:
                st.metric("Ingreso", str(transaccion_actual.ingreso))
            with col4:
                st.metric("Salida", str(transaccion_actual.salida))
            
            st.divider()
            
            # Canvas para firma
            st.write("### ✍️ Dibuja tu firma en el recuadro:")
            st.write("Usa el mouse, dedo o lápiz para firmar")
            st.write("")  # Espacio vertical
            
            try:
                #print("try")
                canvas_result = st_canvas(
                    fill_color="rgba(255, 165, 0, 0.3)",
                    stroke_width=5,
                    stroke_color="black",
                    background_color="#eee",
                    update_streamlit=True,
                    height=300,
                    width=600,
                    drawing_mode="freedraw",
                    key=f"firma_{indice_actual}"
                )
            except Exception as e:
                #print(e)
                st.error(f"Error al cargar el canvas: {str(e)}")
                canvas_result = None
            
            st.write("")  # Espacio vertical
            
            col_limpiar, col_siguiente = st.columns(2)
            """
            with col_limpiar:
                if st.button("🔄 Limpiar", key=f"limpiar_{indice_actual}"):
                    st.rerun()
            """
            """with col_siguiente:
                if st.button("✅ Guardar y Continuar", key=f"siguiente_{indice_actual}"):
                    if canvas_result is not None and canvas_result.image_data is not None:
                        gestor_firmas = GestorFirmas()
                        firma_id = f"{transaccion_actual.fecha}_{transaccion_actual.ingreso}"
                        
                        if gestor_firmas.guardar_firma(canvas_result, firma_id):
                            # Actualizar la transacción con el ID de firma
                            transaccion_actual.firma_id = firma_id
                            # Guardar cambios
                            gestor.guardar()
                            st.success(f"✓ Firma guardada para el registro del {transaccion_actual.fecha}")
                            
                            # Avanzar al siguiente registro
                            st.session_state.indice_firma_actual += 1
                            st.rerun()
                        else:
                            st.error("Error al guardar la firma")
                    else:
                        st.warning("Por favor, dibuja una firma antes de continuar")
                        """
        else:
            st.success("🎉 ¡Todos los registros han sido firmados!")
            if st.button("↻ Volver al inicio", key="reiniciar_firmas"):
                st.session_state.indice_firma_actual = 0
                st.rerun()