
from fastapi import Depends, FastAPI, File, Request, HTTPException, Form, Response, UploadFile, status, APIRouter
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware import Middleware
from sqlalchemy import Double
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
#from excepciones import Exception_No_Apto_Para_Artesano, Exception_No_Apto_Para_Cliente
#from excepcionesUsuario import LoginExpired, Requires_el_Login_de_Exception
import schemas
import  models, seguridad.auth as auth, crudUsuario, crudFrente, crudCandidato, crudEleccion, crudVoto
import seguridad.auth
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from starlette.status import HTTP_303_SEE_OTHER, HTTP_400_BAD_REQUEST
from typing import Annotated, Optional, Union
import shutil
import os
import uuid
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import date, datetime, time, timedelta, timezone
from sqlApp.database import SessionLocal, engine


# Crear todas las tablas en la base de datos
models.Base.metadata.create_all(bind=engine)

# Inicializar la aplicación FastAPI con el middleware de sesión
app = FastAPI(middleware=[
    Middleware(SessionMiddleware, secret_key="your_secret_key")
])

# Montar el directorio estático para servir archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Configurar Jinja2 para la renderización de plantillas
templates = Jinja2Templates(directory="templates")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="iniciar_sesion_post")

# Dependencia para obtener la sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


#Codigo de imagen 

UPLOAD_DIR = "static/images/"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)


def save_upload_file(upload_file: UploadFile, upload_dir: str):
    filename, file_extension = os.path.splitext(upload_file.filename)
    unique_filename = f"{filename}_{uuid.uuid4().hex}{file_extension}"
    file_path = os.path.join(upload_dir, unique_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)

    return file_path


@app.post("/usuario/create/", response_model=schemas.UserBase)
async def crear_usuario_post(request: Request, 
                        CI: str = Form(...), 
                        Nombres: str = Form(...), 
                        Apellidos: str = Form(...), 
                        Estado_vzla: str = Form(...),
                        Correo_electronico: str = Form(...), 
                        Direccion_hab: str = Form(...), 
                        Direccion_electoral: str = Form(...), 
                        Fecha_nacimiento: str = Form(...), 
                        Telefono : str = Form(...),
                        Imagen: UploadFile = File(...),
                        Contrasena : str = Form(...),
                        db: Session = Depends(get_db)):
  
    imagenpath = save_upload_file(Imagen, UPLOAD_DIR)

    print("Usuario: ", Correo_electronico)
    user = schemas.UserCreate(CI=CI, 
                              IdRole="2",
                              Nombres=Nombres, 
                              Apellidos=Apellidos, 
                              Estado_vzla = Estado_vzla,
                              Correo_electronico=Correo_electronico, 
                              Direccion_hab=Direccion_hab,
                              Direccion_electoral=Direccion_electoral, 
                              Fecha_nacimiento=Fecha_nacimiento,
                              Telefono=Telefono,
                              Imagen=imagenpath,
                              Habilitado= True,
                              Contrasena=Contrasena,
                              Estado= "Activo"
                              )
    db_user = crudUsuario.get_user_by_email(db, email=user.Correo_electronico)
    print("Db user: ", db_user)
    if db_user: 
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user = crudUsuario.get_user_by_ci(db, user_id=user.CI)
    if db_user: 
        raise HTTPException(status_code=400, detail="CI already registered")
    crudUsuario.create_user(db=db, user=user)
    return templates.TemplateResponse("crearUsuario.html.jinja", {"request": request})


@app.get("/usuario/create/", response_class=HTMLResponse)
async def create_usuario_template(request: Request, db: Session = Depends(get_db)):
    print("Usuario get: ", )
    roles = crudUsuario.get_roles(db)
    return templates.TemplateResponse("crearUsuario.html.jinja", {"request": request, "Roles": roles})


@app.get("/", response_class=HTMLResponse)
async def home_no_iniciado(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("homeNoIniciado.html.jinja", {"request": request})


@app.get("/user/{user_id}", response_class=HTMLResponse)
async def read_usuario(request: Request, item_id: int, db: Session = Depends(get_db)):
    item = crudUsuario.get_user_by_ci(db, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="User not found")
    return templates.TemplateResponse("perfilUsuario.html", {"request": request, "item": item})

@app.get("/base/administrador/", response_class=HTMLResponse)
async def base_administrador_iniciado(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("baseAdministrador.html.jinja", {"request": request})

@app.get("/base/votante/", response_class=HTMLResponse)
async def base_votante_iniciado(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("baseVotante.html.jinja", {"request": request})

    

# Iniciar sesión
@app.get("/iniciarsesion/", response_class=HTMLResponse)
async def iniciar_sesion_template(request: Request):
    return templates.TemplateResponse("iniciarSesion.html.jinja", {"request": request})



@app.post('/iniciar_sesion', response_class=HTMLResponse)
async def iniciar_sesion_post(request: Request,
                   Correo_electronico: str = Form(...),               
                   Contrasena: str = Form(...), 
                   db: Session = Depends(get_db)):
    user = auth.autenticar_usuario(db, Correo_electronico, Contrasena)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Error, Incorrect username or password',
            headers={"WWW-Authenticate": "Bearer"}
        )
    tiempo_expiracion = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    nombre= f'{user.Nombres} {user.Apellidos}'
    token_acceso = auth.crear_token_acceso(
        data={'CI': user.CI,
              'Nombre': nombre,
              'IdRole': user.IdRole},
        expires_delta=tiempo_expiracion
    )
    request.session['CI'] = user.CI
    request.session['IdRole'] = user.IdRole
    
    print("Rol antess del ciclo", user.IdRole)
    if user.IdRole == 1:
        return RedirectResponse(url="/base/administrador/", status_code=status.HTTP_303_SEE_OTHER)
    elif user.IdRole == 2 or user.IdRole == 3 or user.IdRole == 4 or user.IdRole == 5:
        return RedirectResponse(url="/base/votante/", status_code=status.HTTP_303_SEE_OTHER)
    else:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@app.middleware("http")
async def create_auth_header(request: Request, call_next):
    if ("Authorization" not in request.headers 
        and "Authorization" in request.cookies):
        access_token = request.cookies["Authorization"]
        request.headers.__dict__["_list"].append(
            (
                "authorization".encode(),
                 f"Bearer {access_token}".encode(),
            )
        )
    elif ("Authorization" not in request.headers 
        and "Authorization" not in request.cookies): 
        request.headers.__dict__["_list"].append(
            (
                "authorization".encode(),
                 f"Bearer 12345".encode(),
            )
        )
        
    response = await call_next(request)
    return response



#Frente electoral
@app.post("/front/create/", response_model=schemas.FrontBase)
async def crear_frente_post(request: Request, 
                        Nombre: str = Form(...), 
                        Imagen: UploadFile = File(...),
                        db: Session = Depends(get_db)):
  
    imagenpath = save_upload_file(Imagen, UPLOAD_DIR)

    print("Frente: ", Nombre)
    front = schemas.FrontCreate(
                              Nombre=Nombre,          
                              Imagen=imagenpath
                              )
    crudFrente.create_front(db, front=front)
    fronts = crudFrente.get_fronts(db)
    for front in fronts:
        print('Nombre: ', front.Nombre)
    return templates.TemplateResponse("listaFrenteAdministrador.hml.jinja", {"request": request , "Fronts": fronts})



@app.get("/fronts/list/", response_class=HTMLResponse, name="listar_frentes")
async def listar_frentes(request: Request, db: Session = Depends(get_db)):
    fronts = crudFrente.get_fronts(db)
    if not fronts:
        print("No fronts found")
    else:
        print(f"Found {len(fronts)} fronts")
        for front in fronts:
            print("Front ID:", front.IdFrente)
            print("Front Name:", front.Nombre)
    return templates.TemplateResponse("listaFrenteAdministrador.hml.jinja", {"request": request, "Fronts": fronts})


@app.post("/front/delete/{front_id}/", response_class=HTMLResponse)
async def eliminar_frente(request: Request, front_id: int, db: Session = Depends(get_db)):
    crudFrente.delete_front(db=db, front_id=front_id)
    return RedirectResponse(url='/fronts/list/', status_code=303)

@app.get("/front/create/", response_class=HTMLResponse)
async def crear_frente_template(request: Request, db: Session = Depends(get_db)):
    fronts = crudFrente.get_fronts(db) 
    return templates.TemplateResponse("crearFrenteAdministrador.html.jinja", {"request": request, "Fronts": fronts})


#Elección
@app.post("/election/create/", response_model=schemas.ElectionBase)
async def crear_eleccion_post(request: Request, 
                              Nombre: str = Form(...), 
                              Fecha: date = Form(...), 
                              Hora_apertura: time = Form(...), 
                              Hora_cierre: time = Form(...), 
                              Pob_hab: int = Form(...), 
                              db: Session = Depends(get_db)):

    election = schemas.ElectionCreate(
        Nombre=Nombre,
        Fecha=Fecha,
        Hora_apertura=Hora_apertura,
        Hora_cierre=Hora_cierre,
        Pob_hab=Pob_hab,
        Estado="Activa"
    )
    crudEleccion.create_election(db, election=election)
    elections = crudEleccion.get_elections(db)
    return templates.TemplateResponse("listaEleccionAdministrador.html.jinja", {"request": request, "Elections": elections})

@app.get("/elections/list/", response_class=HTMLResponse, name="listar_elecciones")
async def listar_elecciones(request: Request, db: Session = Depends(get_db)):
    elections = crudEleccion.get_elections(db)
    return templates.TemplateResponse("listaEleccionAdministrador.html.jinja", {"request": request, "Elections": elections})



@app.post("/election/delete/{election_id}/", response_class=HTMLResponse)
async def eliminar_election(request: Request, election_id: int, db: Session = Depends(get_db)):
    crudEleccion.delete_election(db=db, election_id=election_id)
    return RedirectResponse(url='/elections/list/', status_code=303)


@app.get("/election/create/", response_class=HTMLResponse)
async def crear_eleccion_template(request: Request, db: Session = Depends(get_db)):
    elections = crudEleccion.get_elections(db) 
    return templates.TemplateResponse("crearEleccionAdministrador.html.jinja", {"request": request, "Elections": elections})



#Candidato
@app.post("/candidate/create/", response_model=schemas.CandidateBase)
async def crear_candidato_post(
    request: Request,
    IdFrente: int = Form(...),
    IdEleccion: int = Form(...),
    IdUsuario: int = Form(...),
    db: Session = Depends(get_db)
):
   
    candidate = schemas.CandidateCreate(
        IdFrente=IdFrente,
        IdEleccion=IdEleccion,
        IdUsuario=IdUsuario,
        Estado="Habilitado"
    )
    crudCandidato.create_candidate(db, candidate=candidate)
    candidates = crudCandidato.get_candidates_user(db)
    return templates.TemplateResponse("listaCandidatoAdministrador.html.jinja", {"request": request, "Candidates": candidates})


@app.get("/candidates/list/", response_class=HTMLResponse, name="listar_candidatos")
async def listar_candidatos(request: Request, db: Session = Depends(get_db)):
    candidates = crudCandidato.get_candidates_user(db)
    return templates.TemplateResponse("listaCandidatoAdministrador.html.jinja", {"request": request, "Candidates": candidates})

@app.get("/candidates/list/votant", response_class=HTMLResponse, name="listar_candidatos")
async def listar_candidatos_votante(request: Request, db: Session = Depends(get_db)):
    candidates = crudCandidato.get_candidates_user(db)
    return templates.TemplateResponse("tarjetonelectoral.html.jinja", {"request": request, "Candidates": candidates})

@app.post("/candidate/delete/{candidate_id}/", response_class=HTMLResponse)
async def eliminar_candidato(request: Request, candidate_id: int, db: Session = Depends(get_db)):
    crudCandidato.delete_candidate(db=db, candidate_id=candidate_id)
    return RedirectResponse(url='/candidates/list/', status_code=303)

@app.get("/candidate/create/", response_class=HTMLResponse)
async def crear_candidato_template(request: Request, db: Session = Depends(get_db)):
    users = crudUsuario.get_users(db)
    fronts = crudFrente.get_fronts(db)
    elections = crudEleccion.get_elections(db)
    return templates.TemplateResponse("crearCandidato.html.jinja", {"request": request, "Users": users, "Elections": elections, "Fronts": fronts})

#Voto


@app.get("/vote/create/{candidate_id}/{election_id}", response_class=HTMLResponse)
async def voto_seleccionado_template(request: Request, vote_id= int, db: Session = Depends(get_db)):
    vote  = crudVoto.get_vote_by_id(db, vote_id)
    user = crudUsuario.get_users(db) 
    candidate = crudCandidato.get_candidates(db)
    election = crudEleccion.get_elections(db)
    return templates.TemplateResponse("voto.html.jinja", {"request": request, "Vote": vote, "User": user, "Election": election, "Candidate":candidate})




@app.post("/vote/create/", response_model=schemas.VoteBase)
async def crear_voto_post(
    request: Request, 
    IdEleccion: int = Form(...), 
    IdCandidato: int = Form(...), 
    IdVotante: int = Form(...), 
    db: Session = Depends(get_db)
):
    # Validar que la elección existe
    eleccion = crudVoto.get_election_by_id(db, IdEleccion)
    if not eleccion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="La elección no existe")
    
    # Validar que el candidato existe
    candidato = crudVoto.get_candidate_by_id(db, IdCandidato)
    if not candidato:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El candidato no existe")
    
    # Validar que el votante no haya votado previamente en esta elección
    existing_vote = crudVoto.get_vote_by_voter_and_election(db, IdVotante, IdEleccion)
    if existing_vote:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El votante ya ha votado en esta elección")
    

    hora_actual= datetime.now().time()

    # Crear el voto
    vote = schemas.VoteCreate(
        IdEleccion=IdEleccion,          
        IdCandidato=IdCandidato,
        IdVotante=IdVotante,
        Hora= hora_actual
    )
    created_vote = crudVoto.create_vote(db, vote=vote)
    return created_vote

#Resultado
@app.get("/votos/resultado/")
async def obtener_resultado_votos(request: Request, db: Session = Depends(get_db)):
    resultados = crudVoto.sumar_votos(db)
    return templates.TemplateResponse("resultadoVotos.html.jinja", {"request": request, "resultados": resultados})