from datetime import date

import pandas as pd

from clases.GestorTransacciones import GestorTransacciones
from clases.Transaccion import Transaccion


def test_agregar_usuario_valido_y_duplicado(tmp_path):
    archivo_transacciones = tmp_path / "transacciones.csv"
    archivo_usuarios = tmp_path / "usuarios.csv"

    gestor = GestorTransacciones(archivo=str(archivo_transacciones), usar_firestore=False)
    gestor.archivo_usuarios = str(archivo_usuarios)

    assert gestor.agregar_usuario("Juan Perez") is True
    assert gestor.agregar_usuario("juan perez") is False
    assert gestor.obtener_usuarios() == ["JUAN PEREZ"]


def test_guardar_transaccion_con_usuario_en_csv(tmp_path):
    archivo_transacciones = tmp_path / "transacciones.csv"
    archivo_usuarios = tmp_path / "usuarios.csv"

    gestor = GestorTransacciones(archivo=str(archivo_transacciones), usar_firestore=False)
    gestor.archivo_usuarios = str(archivo_usuarios)
    gestor.agregar_usuario("Maria")
    gestor.agregar(
        Transaccion(
            descripcion="LA REYNA - FUNES",
            fecha=date(2026, 10, 1),
            ingreso="16:00",
            salida="00:00",
            usuario="MARIA",
        )
    )

    gestor.guardar()

    df = pd.read_csv(archivo_transacciones)
    assert df.loc[0, "usuario"] == "MARIA"
    assert df.loc[0, "descripcion"] == "LA REYNA - FUNES"


def test_cargar_usuarios_y_transacciones_desde_csv(tmp_path):
    archivo_transacciones = tmp_path / "transacciones.csv"
    archivo_usuarios = tmp_path / "usuarios.csv"

    pd.DataFrame(
        [
            {
                "usuario": "ANA",
                "descripcion": "OBRA 1",
                "fecha": "2026-10-02",
                "ingreso": "08:00",
                "salida": "17:00",
                "firma_id": "",
            }
        ]
    ).to_csv(archivo_transacciones, index=False)
    pd.DataFrame([{"nombre": "ANA"}, {"nombre": "LUIS"}]).to_csv(archivo_usuarios, index=False)

    gestor = GestorTransacciones(archivo=str(archivo_transacciones), usar_firestore=False)
    gestor.archivo_usuarios = str(archivo_usuarios)
    gestor.cargar()

    assert gestor.obtener_usuarios() == ["ANA", "LUIS"]
    assert len(gestor.transacciones) == 1
    assert gestor.transacciones[0].usuario == "ANA"
