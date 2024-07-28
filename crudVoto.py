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
    return db.query(models.Eleccion).filter(models.Eleccion.Id_Eleccion == election_id).first()

def get_candidate_by_id(db: Session, candidate_id: int):
    return db.query(models.Candidato).filter(models.Candidato.IdCandidato == candidate_id).first()

def get_elections(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Eleccion).offset(skip).limit(limit).all()


def sumar_votos(db: Session):
    # Query to get total votes per candidate and total votes in the election
    results = (
        db.query(
            models.Candidato.IdEleccion,
            models.Eleccion.Nombre.label("eleccion_nombre"),
            models.Candidato.IdCandidato,
            models.Usuario.Nombres.label("candidato_nombre"),
            models.Usuario.Imagen.label("candidato_imagen"), 
            func.count(models.Voto.IdVoto).label("total_votos"),
            models.Eleccion.Pob_hab.label("pob_hab"),
            (func.count(models.Voto.IdVoto) / models.Eleccion.Pob_hab * 100).label("participation_rate"),
        )
        .join(models.Candidato, models.Voto.IdCandidato == models.Candidato.IdCandidato)
        .join(models.Eleccion, models.Voto.IdEleccion == models.Eleccion.Id_Eleccion)
        .join(models.Usuario, models.Candidato.IdUsuario == models.Usuario.CI)
        .group_by(
            models.Candidato.IdEleccion,
            models.Eleccion.Nombre,
            models.Candidato.IdCandidato,
            models.Usuario.Nombres,
            models.Usuario.Imagen, 
            models.Eleccion.Pob_hab
        )
        .all()
    )
    
    # Query to get the total number of votes
    total_votes = db.query(func.count(models.Voto.IdVoto)).scalar()
    
    return results, total_votes