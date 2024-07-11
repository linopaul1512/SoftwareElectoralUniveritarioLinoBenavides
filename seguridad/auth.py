"""from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
#from dependencias import get_db 
import crudUsuario, models, schemas
from sqlApp.database import SessionLocal
from typing import Union
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi import Security
#from excepcionesUsuario import LoginExpired, Requires_el_Login_de_Exception


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
    if not verificar_contrasena(password, usuario.contrasena):
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
    user = db.query(models.Usuario).filter(models.Usuario.cedula_identidad == user_id).first()
    if user is None:
        return {"ok": False, "mensaje": "User not found"}
    usuario = schemas.User(
        cedula_identidad = user.cedula_identidad,
        nombre = user.nombre,
        apellido = user.apellido,
        direccion=user.direccion,
        fecha_nacimiento=user.fecha_nacimiento,
        correo_electronico=user.correo_electronico,
        contrasena=user.contrasena,
        tipo_usuario=user.tipo_usuario
    )
    return {"ok": True, "mensaje": "User found", "data": usuario}




#Esto es para el perfil
async def obtener_usuario_actual(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credenciales_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credenciales_exception
    except JWTError:
        raise credenciales_exception
    usuario = crudUsuario.get_user_by_email(db, email)
    if usuario is None:
        raise credenciales_exception
    return usuario



async def obtener_usuario_activo_actual(usuario_actual: models.Usuario = Depends(obtener_usuario_actual)):
    return usuario_actual


    

"""