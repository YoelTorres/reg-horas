from __future__ import annotations

from fpdf import FPDF
import pandas as pd

from clases.GestorFirmas import GestorFirmas


class PlanillaPDF(FPDF):
    """Generates the hours summary PDF."""

    def __init__(self) -> None:
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
        dias: int = 31,
    ) -> bytes:
        """Build the PDF document in memory."""
        self.add_page()
        self.set_line_width(0.45)
        self.rect(10, 5, 190, 282)

        self.line(10, 25, 200, 25)
        self.line(10, 35, 200, 35)

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

        self.set_font("Helvetica", "B", 12)
        self.set_xy(75, 10)
        self.cell(143, 9, "PLANILLA CONTROL HORARIO", align="L")

        self.set_font("Helvetica", "", 10)
        self.set_xy(150, 6)
        self.cell(48, 10, "Registro: R-08.06")
        self.set_xy(150, 11)
        self.cell(42, 10, "Fecha: 08/02/2022")
        self.set_xy(150, 16)
        self.cell(30, 10, "Revisión: 00")

        self.set_font("Helvetica", "", 12)
        self.set_xy(12, 25)
        self.cell(185, 10, f"Nombre y Apellido: {nombre_apellido}")
        self.set_xy(12, 35)
        self.cell(175, 10, f"Mes: {mes} {anio}")

        x = 10
        y = 40
        header_height = 10
        widths = [10, 35, 55, 45, 45]
        headers = ["DÍA", "USUARIO", "LUGAR", "INGRESO", "SALIDA"]

        self.set_font("Helvetica", "B", 10)
        current_x = x
        for width, header in zip(widths, headers):
            self.set_xy(current_x, y + 6)
            self.multi_cell(width, h=header_height, text=header, border=1, align="C")
            current_x += width

        df = df.copy()
        df["DIA"] = pd.to_datetime(df["fecha"])
        df["DIA_NUM"] = df["DIA"].dt.day
        df = df.drop_duplicates(subset=["DIA_NUM"], keep="last")
        datos_por_dia = df.set_index("DIA_NUM").to_dict("index")

        row_y = y + 16
        row_height = 7.45
        self.set_font("Helvetica", "", 7)
        self.set_line_width(0.25)

        for dia in range(1, dias + 1):
            current_x = x
            datos = datos_por_dia.get(dia, {})
            ingreso = datos.get("ingreso", "")
            egreso = datos.get("salida", "")
            lugar = datos.get("descripcion", "")
            usuario = datos.get("usuario", "")

            for width in widths:
                self.rect(current_x, row_y, width, row_height)
                current_x += width

            self.set_xy(x, row_y)
            self.cell(widths[0], row_height, str(dia), align="C")

            self.set_xy(x + widths[0], row_y)
            self.cell(widths[1], row_height, str(usuario), align="L")

            self.set_xy(x + widths[0] + widths[1], row_y)
            self.cell(widths[2], row_height, str(lugar), align="L")

            self.set_xy(x + widths[0] + widths[1] + widths[2], row_y)
            self.cell(widths[3], row_height, str(ingreso), align="L")

            self.set_xy(x + widths[0] + widths[1] + widths[2] + widths[3], row_y)
            self.cell(widths[4], row_height, str(egreso), align="L")

            row_y += row_height

        return bytes(self.output())
