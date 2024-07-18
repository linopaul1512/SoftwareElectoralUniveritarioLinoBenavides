from typing import Optional, TypeVar, Generic
from pydantic import BaseModel
from datetime import date, time

T = TypeVar('T')

class UserBase(BaseModel):
    CI: str
    IdRole: int
    Nombres: str
    Apellidos: str
    Fecha_nacimiento: date
    Estado_vzla:str
    Correo_electronico: str
    Direccion_electoral: str
    Direccion_hab:str
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
    CI: int

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
    IdEleccion: int
    IdUsuario: int
    Hora: time
    Estado: str
   
class  CandidateCreate(CandidateBase):
   pass

class CandidateUpdate(CandidateBase):
   IdCandidato: int

class Candidate(CandidateBase):
   

    class Config:
        orm_mode = True