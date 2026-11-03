from datetime import date

import pandas as pd

from clases.GestorTransacciones import GestorTransacciones
from clases.Transaccion import Transaccion


def test_transaccion_serializa_usuario() -> None:
    transaccion = Transaccion(
        descripcion="LA REYNA - FUNES",
        fecha=date(2026, 10, 1),
        ingreso="16:00",
        salida="00:00",
        usuario="MICAELA SANTA MARIA",
    )

    data = transaccion.to_dict()

    assert data["usuario"] == "MICAELA SANTA MARIA"


def test_transaccion_deserializa_usuario() -> None:
    data = {
        "descripcion": "LA REYNA - FUNES",
        "fecha": "2026-10-01",
        "ingreso": "16:00",
        "salida": "00:00",
        "firma_id": "",
        "usuario": "MICAELA SANTA MARIA",
    }

    transaccion = Transaccion.from_dict(data)

    assert transaccion.usuario == "MICAELA SANTA MARIA"


def test_gestor_guarda_y_carga_usuario_en_csv(tmp_path) -> None:
    archivo = tmp_path / "transacciones.csv"
    gestor = GestorTransacciones(archivo=str(archivo), usar_firestore=False)
    gestor.agregar(
        Transaccion(
            descripcion="LA REYNA - FUNES",
            fecha=date(2026, 10, 1),
            ingreso="16:00",
            salida="00:00",
            usuario="MICAELA SANTA MARIA",
        )
    )

    gestor.guardar()

    df = pd.read_csv(archivo)
    assert "usuario" in df.columns
    assert df.iloc[0]["usuario"] == "MICAELA SANTA MARIA"

    nuevo_gestor = GestorTransacciones(archivo=str(archivo), usar_firestore=False)
    nuevo_gestor.cargar()

    assert len(nuevo_gestor.transacciones) == 1
    assert nuevo_gestor.transacciones[0].usuario == "MICAELA SANTA MARIA"
