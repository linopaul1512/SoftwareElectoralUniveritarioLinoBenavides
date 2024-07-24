from sqlalchemy.orm import Session
import models
from pydantic import Field
from sqlalchemy.orm import Session
import schemas
from schemas import Respuesta, Token


def create_front(db: Session, front: schemas.FrontCreate):
    db_front = models.Frente(
        Nombre=front.Nombre,
        Imagen=front.Imagen
    )
    db.add(db_front)
    db.commit()
    db.refresh(db_front)
    return db_front

def get_front_by_id(db: Session, front_id: int):
    return db.query(models.Frente).filter(models.Frente.IdFrente == front_id).first()


def delete_front(db: Session, front_id: int):
    db_front = get_front_by_id(db, front_id)
    if db_front is None:
        return None
    db.delete(db_front)
    db.commit()
    return db_front

def get_fronts(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Frente).offset(skip).limit(limit).all()
