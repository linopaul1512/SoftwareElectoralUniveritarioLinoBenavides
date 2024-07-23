from sqlalchemy.orm import Session
import models
from pydantic import Field
from passlib.context import CryptContext
import schemas
from schemas import Respuesta, Token



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    return pwd_context.hash(password)


def create_user(db: Session, user: schemas.UserCreate):
        db_user = models.Usuario(
        CI = user.CI,
        IdRole= user.IdRole,
        Nombres= user.Nombres,
        Apellidos= user.Apellidos,
        Fecha_nacimiento= user.Fecha_nacimiento,
        Correo_electronico= user.Correo_electronico,
        Direccion_electoral= user.Direccion_electoral,
        Estado_vzla= user.Estado_vzla,
        Direccion_hab= user.Direccion_hab,
        Telefono= user.Telefono,
        Habilitado= user.Habilitado,
        Contrasena = get_password_hash(user.Contrasena), 
        Imagen= user.Imagen,
        Estado= user.Estado
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        real_user = schemas.User(
        CI = db_user.CI,
        IdRole= db_user.IdRole,
        Nombres= db_user.Nombres,
        Apellidos= db_user.Apellidos,
        Fecha_nacimiento= db_user.Fecha_nacimiento,
        Correo_electronico= db_user.Correo_electronico,
        Direccion_electoral= db_user.Direccion_electoral,
        Direccion_hab= db_user.Direccion_hab,
        Estado_vzla=db_user.Estado_vzla,
        Telefono= db_user.Telefono,
        Habilitado= db_user.Habilitado,
        Contrasena = db_user.Contrasena, 
        Imagen= db_user.Imagen,
        Estado= db_user.Estado
        )
        respuesta = Respuesta[schemas.User](
            ok=True, 
            mensaje='Usuario registrado exitósamente. ADVERTENCIA: ESTA ES LA ÚLTIMA VEZ QUE VERÁ SU CONTRASEÑA LIBREMENTE', 
            data=real_user
        )
        return respuesta            


    

def buscar_usuario(db: Session, user_id: str): 
    user_return = db.query(models.Usuario).filter(models.Usuario.CI == user_id).first()

    if user_return == None:
        return Respuesta[schemas.User](ok=False, mensaje='Usuario no encontrado')

    user = schemas.User(
        CI = user_return.CI,
        IdRole= user_return.IdRole,
        Nombres= user_return.Nombres,
        Apellidos= user_return.Apellidos,
        Fecha_nacimiento= user_return.Fecha_nacimiento,
        Correo_electronico= user_return.Correo_electronico,
        Direccion_electoral= user_return.Direccion_electoral,
        Direccion_hab= user_return.Direccion_hab,
        Estado_vzla=user_return.Estado_vzla,
        Telefono= user_return.Telefono,
        Habilitado= user_return.Habilitado,
        Contrasena = user_return.Contrasena, 
        Imagen= user_return.Imagen,
        Estado= user_return.Estado
    )
    
    return Respuesta[schemas.User](ok=True, mensaje='Usuario encontrado', data=user)


def get_user_by_email(db: Session, email: str):
    print("Get email: ", email)
    return db.query(models.Usuario).filter(models.Usuario.Correo_electronico == email).first()


def get_user_by_ci(db: Session, user_id: int):
    return db.query(models.Usuario).filter(models.Usuario.Correo_electronico == user_id).first()


def update_user(db: Session, user_id: int, user: schemas.UserUpdate):
    db_user = get_user_by_ci(db, user_id)
    if db_user is None:
        return None
    for key, value in user.dict().items():
        if value:
            if key == 'Contrasena':
                setattr(db_user, key, get_password_hash(value))
            else:
                setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int):
    db_user = get_user_by_ci(db, user_id)
    if db_user is None:
        return None
    db.delete(db_user)
    db.commit()
    return db_user

def obtener_usuario(db: Session, user_id: str):
    return db.query(models.Usuario).filter(models.Usuario.CI == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Usuario).offset(skip).limit(limit).all()

def get_roles(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Rol).offset(skip).limit(limit).all()
