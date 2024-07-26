from sqlalchemy import func
from sqlalchemy.orm import Session
import models
import schemas

def create_vote(db: Session, vote: schemas.VoteCreate):
    db_vote = models.Voto(
        IdEleccion=vote.IdEleccion,
        IdCandidato=vote.IdCandidato,
        IdVotante=vote.IdVotante,
        Hora=vote.Hora
    )
    db.add(db_vote)
    db.commit()
    db.refresh(db_vote)
    return db_vote

def get_vote_by_id(db: Session, vote_id: int):
    return db.query(models.Voto).filter(models.Voto.IdVoto == vote_id).first()

def get_vote_by_voter_and_election(db: Session, IdVotante: int, IdEleccion: int):
    return db.query(models.Voto).filter(
        models.Voto.IdVotante == IdVotante,
        models.Voto.IdEleccion == IdEleccion
    ).first()

def delete_vote(db: Session, vote_id: int):
    db_vote = get_vote_by_id(db, vote_id)
    if db_vote is None:
        return None
    db.delete(db_vote)
    db.commit()
    return db_vote

def get_election_by_id(db: Session, election_id: int):
    return db.query(models.Eleccion).filter(models.Eleccion.IdEleccion == election_id).first()

def get_candidate_by_id(db: Session, candidate_id: int):
    return db.query(models.Candidato).filter(models.Candidato.IdCandidato == candidate_id).first()

def get_elections(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Eleccion).offset(skip).limit(limit).all()



def sumar_votos(db: Session):
    resultados = db.query(
        models.Eleccion.Nombre.label('eleccion_nombre'),
        models.Usuario.Nombres.label('candidato_nombre'),
        func.count(models.Voto.IdVoto).label('total_votos')
    ).join(models.Candidato, models.Candidato.IdCandidato == models.Voto.IdCandidato)\
     .join(models.Usuario, models.Usuario.CI == models.Candidato.IdUsuario)\
     .join(models.Eleccion, models.Eleccion.Id_Eleccion == models.Voto.IdEleccion)\
     .group_by(models.Eleccion.Nombre, models.Usuario.Nombres).all()

    return resultados