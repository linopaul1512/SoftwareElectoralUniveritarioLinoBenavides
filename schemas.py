from typing import Optional, TypeVar, Generic
from pydantic import BaseModel
from datetime import date, time

T = TypeVar('T')

class UserBase(BaseModel):
    CI: int
    IdRole: int
    Nombres: str
    Apellidos: str
    Fecha_nacimiento: date
    Estado_vzla: str
    Correo_electronico: str
    Direccion_electoral: str
    Direccion_hab: str
    Telefono: str
    Habilitado: bool
    Contrasena: str
    Imagen: str
    Estado: str

class UserCreate(UserBase):
    pass

class UserUpdate(UserBase):
    Contrasena: str

class User(UserBase):
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    Correo_electronico: Optional[str] = None

# Respuesta con datos genéricos
class Respuesta(Generic[T], BaseModel):
    ok: bool
    mensaje: str
    data: Optional[T]

    class Config:
        arbitrary_types_allowed = True

class FrontBase(BaseModel):
    Nombre: str
    Imagen: str

class FrontCreate(FrontBase):
    pass

class FrontUpdate(FrontBase):
    IdFrente: int

class Front(FrontBase):
    class Config:
        orm_mode = True

class CandidateBase(BaseModel):
    IdFrente: int
    Id_Eleccion: int
    IdUsuario: int
    Estado: str

class CandidateCreate(CandidateBase):
    pass

class CandidateUpdate(CandidateBase):
    IdCandidato: int

class Candidate(CandidateBase):
    class Config:
        orm_mode = True

class ElectionBase(BaseModel):
    Fecha: date
    Nombre: str
    Hora_apertura: time
    Hora_cierre: time
    Pob_hab: int
    Estado: str

class ElectionCreate(ElectionBase):
    pass

class ElectionUpdate(ElectionBase):
    Id_Eleccion: int

class Election(ElectionBase):
    class Config:
        orm_mode = True


class VoteBase(BaseModel):
    IdVoto: int
    IdEleccion: int
    IdCandidato: int
    IdVotante: int
    Hora: time

class VoteCreate(VoteBase):
    pass

class VoteUpdate(VoteBase):
    IdVoto: int

class Vote(VoteBase):
    class Config:
        orm_mode = True
