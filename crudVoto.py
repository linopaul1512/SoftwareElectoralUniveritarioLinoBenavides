from sqlalchemy.orm import Session
import models
from pydantic import Field
from sqlalchemy.orm import Session
import schemas
from schemas import Respuesta, Token


def create_vote(db: Session, vote: schemas.VoteCreate):
    db_vote = models.Eleccion(
        IdEleccion=vote.IdEleccion,
        IdCandidato=vote.IdCandidato,
        IdVotante=vote.IdVotante,
        Hora=vote.Hora
    )
    db.add(db_vote)
    db.commit()
    db.refresh(db_vote)
    return db_vote

def get_vote_by_id(db: Session,  vote_id: int):
    return db.query(models.Voto).filter(models.Voto.IdEleccion == vote_id).first()


def delete_vote(db: Session, vote_id: int):
    db_vote = get_vote_by_id(db, vote_id)
    if db_vote is None:
        return None
    db.delete(db_vote)
    db.commit()
    return db_vote

def get_elections(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Eleccion).offset(skip).limit(limit).all()
