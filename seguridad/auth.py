from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from dependencias import get_db 
import crudUsuario, models, schemas
from sqlApp.database import SessionLocal
from typing import Union
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi import Security
from excepcionesUsuario import LoginExpired, Requires_el_Login_de_Exception


SECRET_KEY = "27A0D7C4CCCE76E6BE39225B7EEE8BD0EF890DE82D49E459F4C405C583080AB0"  
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verificar_contrasena(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def obtener_hash_contrasena(password):
    return pwd_context.hash(password)



def autenticar_usuario(db: Session, email: str, password: str):
    usuario = crudUsuario.get_user_by_email(db, email)
    if not usuario:
        return False
    if not verificar_contrasena(password, usuario.Contrasena):
        return False
    return usuario


def crear_token_acceso(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def buscar_usuario(db: Session, user_id: str):
    user = db.query(models.Usuario).filter(models.Usuario.CI == user_id).first()
    if user is None:
        return {"ok": False, "mensaje": "User not found"}
    usuario = schemas.User(
        CI = user.CI,
        IdRole =user.IdRole,
        Nombres = user.Nombres,
        Apellidos = user.Apellidos,
        Correo_electronico=user.Correo_electronico,
        Estado_vzla=user.Estado_vzla,
        Direccion_hab=user.Direccion_hab,
        Direccion_electoral=user.Direccion_electoral,
        Fecha_nacimiento=user.Fecha_nacimiento,
        Telefono=user.Telefono,
        Imagen=user.Imagen,
        Habilitado=user.Habilitado,
        Contrasena=user.Contrasena,
        Estado=user.Estado
    )
    return {"ok": True, "mensaje": "User found", "data": usuario}








    

