from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date, Time
from sqlalchemy.orm import relationship
from sqlApp.database import Base


class Rol(Base):
    __tablename__ = 'roles'
    IdRole = Column(Integer, primary_key=True)
    Nombre = Column(String(100), nullable=False)

    usuarios = relationship("Usuario", back_populates="rol")


class Usuario(Base):
    __tablename__ = 'usuarios'
    CI = Column(Integer, primary_key=True)
    IdRole = Column(Integer, ForeignKey('roles.IdRole'), nullable=False)
    Nombres = Column(String(100), nullable=False)
    Apellidos = Column(String, nullable=False)
    Correo_electronico = Column(String(50), nullable=False)
    Estado_vzla = Column(String(50), nullable=False)
    Direccion_hab = Column(String(50), nullable=False)
    Direccion_electoral = Column(String(50), nullable=False)
    Fecha_nacimiento = Column(Date, nullable=False)
    Telefono = Column(String(50), nullable=False)
    Imagen = Column(String(255), nullable=False)
    Habilitado = Column(Boolean, nullable=False)
    Contrasena = Column(String(255), nullable=False)
    Estado = Column(String(255), nullable=False)

    rol = relationship("Rol", back_populates="usuarios")
    candidatos = relationship("Candidato", back_populates="usuario")
    votos = relationship("Voto", back_populates="usuario")


class Frente(Base):
    __tablename__ = 'frentes'
    IdFrente = Column(Integer, primary_key=True)
    Nombre = Column(String(255), nullable=False)
    Imagen = Column(String(255), nullable=False)

    candidatos = relationship("Candidato", back_populates="frente")


class Eleccion(Base):
    __tablename__ = 'elecciones'
    Id_Eleccion = Column(Integer, primary_key=True)
    Fecha = Column(Date, nullable=False)
    Hora_apertura = Column(Time, nullable=False)
    Hora_cierre = Column(Time, nullable=False)
    Pob_hab = Column(Integer, nullable=False)
    Estado = Column(String(255), nullable=False)
    Nombre = Column(String(255), nullable=False)
   
    candidatos = relationship("Candidato", back_populates="eleccion")
    votos = relationship("Voto", back_populates="eleccion")


class Candidato(Base):
    __tablename__ = 'candidatos'
    IdCandidato = Column(Integer, primary_key=True)
    IdFrente = Column(Integer, ForeignKey('frentes.IdFrente'), nullable=False)
    IdEleccion = Column(Integer, ForeignKey('elecciones.Id_Eleccion'), nullable=False)
    IdUsuario = Column(Integer, ForeignKey('usuarios.CI'), nullable=False)
    Estado = Column(String(255), nullable=False)

    usuario = relationship("Usuario", back_populates="candidatos")
    frente = relationship("Frente", back_populates="candidatos")
    eleccion = relationship("Eleccion", back_populates="candidatos")
    votos = relationship("Voto", back_populates="candidato")


class Voto(Base):
    __tablename__ = 'votos'
    IdVoto = Column(Integer, primary_key=True)
    IdEleccion = Column(Integer, ForeignKey('elecciones.Id_Eleccion'), nullable=False)
    IdCandidato = Column(Integer, ForeignKey('candidatos.IdCandidato'), nullable=False)
    IdVotante = Column(Integer, ForeignKey('usuarios.CI'), nullable=False)
    Hora = Column(Time, nullable=False)

    eleccion = relationship("Eleccion", back_populates="votos")
    candidato = relationship("Candidato", back_populates="votos")
    usuario = relationship("Usuario", back_populates="votos")

