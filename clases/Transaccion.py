from __future__ import annotations

from datetime import date
from typing import Any, Dict


class Transaccion:
    """Modelo de una transacción individual."""

    def __init__(
        self,
        descripcion: str,
        fecha: date,
        ingreso: str,
        salida: str,
        usuario: str = "",
        firma_id: str = "",
    ) -> None:
        self.descripcion = descripcion
        self.fecha = fecha
        self.ingreso = ingreso
        self.salida = salida
        self.usuario = usuario
        self.firma_id = firma_id

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the transaction to a dictionary."""
        return {
            "usuario": self.usuario,
            "descripcion": self.descripcion,
            "fecha": str(self.fecha),
            "ingreso": self.ingreso,
            "salida": self.salida,
            "firma_id": self.firma_id,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Transaccion":
        """Build a transaction from a dictionary."""
        raw_fecha = data["fecha"]
        fecha = raw_fecha if isinstance(raw_fecha, date) else date.fromisoformat(str(raw_fecha))
        return cls(
            descripcion=str(data["descripcion"]),
            fecha=fecha,
            ingreso=str(data["ingreso"]),
            salida=str(data["salida"]),
            usuario=str(data.get("usuario", "")),
            firma_id=str(data.get("firma_id", "")),
        )
