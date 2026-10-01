from datetime import date
from typing import Dict


class Transaccion:
    """Modelo de una transacción individual."""

    def __init__(self, descripcion: str, fecha: date, ingreso: str, salida: str, firma_id: str = ""):
        self.descripcion = descripcion
        self.fecha = fecha
        self.ingreso = ingreso
        self.salida = salida
        self.firma_id = firma_id

    def to_dict(self) -> Dict:
        return {
            "descripcion": self.descripcion,
            "fecha": str(self.fecha),  # Convertir date a string (YYYY-MM-DD)
            "ingreso": self.ingreso,
            "salida": self.salida,
            "firma_id": self.firma_id
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Transaccion":
        return cls(
            descripcion=data["descripcion"],
            fecha=data["fecha"] if isinstance(data["fecha"], date) else date.fromisoformat(str(data["fecha"])),
            ingreso=data["ingreso"],
            salida=data["salida"],
            firma_id=data.get("firma_id", "")
        )