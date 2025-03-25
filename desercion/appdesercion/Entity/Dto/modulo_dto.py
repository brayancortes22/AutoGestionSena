from dataclasses import dataclass
import datetime


@dataclass
class ModuloDTO:
    id: int
    nombre: str
    descripcion: str
    icono: str
    fechaCreo: datetime
    fechaModifico: datetime | None # type: ignore
    fechaElimino: datetime | None # type: ignore