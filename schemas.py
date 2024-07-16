from typing import Optional, TypeVar, Generic
from pydantic import BaseModel
from datetime import date

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
    Habilitado: str
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
