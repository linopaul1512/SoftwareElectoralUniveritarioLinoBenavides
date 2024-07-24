from sqlalchemy.orm import Session
import models
from pydantic import Field
from sqlalchemy.orm import Session
import schemas
from schemas import Respuesta, Token


def create_election(db: Session, election: schemas.ElectionCreate):
    db_election = models.Eleccion(
        Fecha=election.Fecha,
        Hora_apertura=election.Hora_apertura,
        Hora_cierre= election.Hora_cierre,
        Pob_hab= election.Pob_hab,
        Estado=election.Estado
    )
    db.add(db_election)
    db.commit()
    db.refresh(db_election)
    return db_election

def get_election_by_id(db: Session, election_id: int):
    return db.query(models.Eleccion).filter(models.Eleccion.Id_Eleccion == election_id).first()


def delete_election(db: Session, election_id: int):
    db_election = get_election_by_id(db, election_id)
    if db_election is None:
        return None
    db.delete(db_election)
    db.commit()
    return db_election

def get_elections(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Eleccion).offset(skip).limit(limit).all()
