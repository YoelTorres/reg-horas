import os

from fpdf import FPDF
import pandas as pd
from numpy.f2py.crackfortran import endifs
from clases.GestorFirmas import GestorFirmas


class PlanillaPDF(FPDF):

    def __init__(self):
        super().__init__("P", "mm", "A4")
        self.set_auto_page_break(False)
        self.set_margins(10, 10, 10)
        self.gestor_firmas = GestorFirmas()

    def generar(
        self,
        nombre_apellido: str,
        mes: str,
        anio: int,
        df: pd.DataFrame,
        dias: int = 31
    ) -> bytes:

        self.add_page()

        # =========================
        # MARCO GENERAL
        # =========================

        self.set_line_width(0.45)
        self.rect(10, 5, 190, 282)

        # =========================
        # EMPRESA / LOGO
        # =========================

        self.line(10,25, 200,25)
        self.line(10, 35, 200, 35)

        # Logo simple
        self.set_line_width(0.8)
        self.ellipse(17, 6.5, 17, 17)

        self.set_font("Helvetica", "B", 35)
        self.set_xy(21, 9)
        self.cell(9, 13, "N", align="C")

        self.set_font("Helvetica", "B", 10)

        self.set_xy(34.5, 7)
        self.cell(24, 9, "NV SERVICIOS", align="L")

        self.set_xy(34.5, 12)
        self.cell(24, 9, "PROFESIONALES", align="L")

        self.set_xy(34.5, 17)
        self.cell(24, 9, "DE LIMPIEZA", align="L")

        # =========================
        # TITULO
        # =========================

        self.set_font("Helvetica", "B", 12)
        self.set_xy(75, 10)

        self.cell(
            143,
            9,
            "PLANILLA CONTROL HORARIO",
            align="L"
        )

        # =========================
        # DATOS DEL FORMULARIO
        # =========================

        self.set_font("Helvetica", "", 10)

        self.set_xy(150, 6)
        self.cell(48, 10, "Registro: R-08.06")
        self.set_xy(150, 11)
        self.cell(42, 10, "Fecha: 08/02/2022")
        self.set_xy(150, 16)
        self.cell(30, 10, "Revisión: 00")

        # =========================
        # DATOS EMPLEADO
        # =========================

        self.set_font("Helvetica", "", 12)

        self.set_xy(12, 25)
        self.cell(
            185,
            10,
            f"Nombre y Apellido: {nombre_apellido}"
        )

        self.set_xy(12, 35)
        self.cell(
            175,
            10,
            f"Mes: {mes} {anio}"
        )

        # =========================
        # TABLA
        # =========================

        x = 10
        y = 40

        header_height = 10

        widths = [
            10,  # DIA
            90,  # LUGAR
            45,  # INGRESO
            45,  # SALIDA
            10,  # FIRMA
        ]

        headers = [
            "DÍA",
            "LUGAR",
            "INGRESO",
            "SALIDA",
            "FIRMA"
        ]

        self.set_font("Helvetica", "B", 10)

        current_x = x

        for width, header in zip(widths, headers):

            """self.rect(
                current_x,
                y,
                width,
                header_height
            )"""

            self.set_xy(
                current_x,
                y + 6
            )

            self.multi_cell(
                width,
                h=header_height,
                text=header,
                border=1,
                align="C"
            )

            current_x += width

        # =========================
        # PREPARAR DATAFRAME
        # =========================

        df = df.copy()

        # Si DIA es una fecha:
        df["DIA"] = pd.to_datetime(df["fecha"])

        # Obtener solamente el número del día
        df["DIA_NUM"] = df["DIA"].dt.day

        # Crear índice por día
        datos_por_dia = df.set_index("DIA_NUM").to_dict("index")
        # =========================
        # FILAS
        # =========================

        row_y = y + 16

        row_height = 7.45

        self.set_font("Helvetica", "", 7)
        self.set_line_width(0.25)

        for dia in range(1, dias + 1):

            current_x = x

            # Buscar información del día
            datos = datos_por_dia.get(dia, {})
            if datos == None:
                continue

            ingreso = datos.get("ingreso", "")
            egreso = datos.get("salida", "")
            lugar = datos.get("descripcion", "")
            firma_id = datos.get("firma_id", "")


            # Dibujar celdas
            for width in widths:
                self.rect(
                    current_x,
                    row_y,
                    width,
                    row_height
                )

                current_x += width

            # =========================
            # DIA
            # =========================

            self.set_xy(x, row_y)

            self.cell(
                widths[0],
                row_height,
                str(dia),
                align="C"
            )

            # =========================
            # LUGAR
            # =========================

            self.set_xy(
                x + widths[0],
                row_y
            )

            self.cell(
                widths[1],
                row_height,
                str(lugar),
                align="L"
            )

            # =========================
            # INGRESO
            # =========================

            self.set_xy(
                x + widths[0]+ widths[1],
                row_y
            )

            self.cell(
                widths[2],
                row_height,
                str(ingreso),
                align="L"
            )

            # =========================
            # EGRESO
            # =========================

            self.set_xy(
                x + widths[0] + widths[1]+ widths[2],
                row_y
            )

            self.cell(
                widths[3],
                row_height,
                str(egreso),
                align="L"
            )

            # =========================
            # FIRMA
            # =========================

            if firma_id and self.gestor_firmas.firma_existe(firma_id):
                ruta_firma = self.gestor_firmas.obtener_ruta_firma(firma_id)
                try:
                    self.image(
                        ruta_firma,
                        x + widths[0] + widths[1] + widths[2] + widths[3] + 1,
                        row_y + 1,
                        w=widths[4] - 2,
                        h=row_height - 2
                    )
                except Exception as e:
                    print(f"Error al insertar firma: {str(e)}")

            row_y += row_height
        # =========================
        # DEVOLVER PDF EN MEMORIA
        # =========================

        return bytes(self.output())