# crudCandidato.py

from sqlalchemy.orm import Session
import models
import schemas

def create_candidate(db: Session, candidate: schemas.CandidateCreate):
    db_candidate = models.Candidato(
        IdFrente=candidate.IdFrente,
        IdEleccion=candidate.IdEleccion,
        IdUsuario=candidate.IdUsuario,
        Estado=candidate.Estado
    )
    db.add(db_candidate)
    db.commit()
    db.refresh(db_candidate)
    return db_candidate

def get_candidate_by_id(db: Session, candidate_id: int):
    return db.query(models.Candidato).filter(models.Candidato.IdFrente == candidate_id).first()

def get_candidates_user(db: Session):
    return db.query(models.Candidato, models.Usuario, models.Eleccion, models.Frente)\
        .join(models.Usuario, models.Candidato.IdUsuario == models.Usuario.CI)\
        .join(models.Eleccion, models.Candidato.IdEleccion == models.Eleccion.Id_Eleccion)\
        .join(models.Frente, models.Candidato.IdFrente == models.Frente.IdFrente)\
        .filter(models.Eleccion.Estado == "Activa").all()

def delete_candidate(db: Session, candidate_id: int):
    db_candidate = get_candidate_by_id(db, candidate_id)
    if db_candidate is None:
        return None
    db.delete(db_candidate)
    db.commit()
    return db_candidate

def get_candidates(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Candidato).offset(skip).limit(limit).all()

def get_candidates_votant(db: Session):
    return db.query(models.Candidato, models.Usuario, models.Eleccion)\
        .join(models.Usuario, models.Candidato.IdUsuario == models.Usuario.CI)\
        .join(models.Eleccion, models.Candidato.IdEleccion == models.Eleccion.Id_Eleccion)\
        .all()
