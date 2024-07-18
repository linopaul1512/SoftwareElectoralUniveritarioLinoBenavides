
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
import  models, seguridad.auth as auth, crudUsuario, crudFrente, crudCandidato
import seguridad.auth
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from starlette.status import HTTP_303_SEE_OTHER, HTTP_400_BAD_REQUEST
from typing import Annotated, Optional, Union
import shutil
import os
import uuid
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import date, datetime, timedelta, timezone
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
                              IdRole="1",
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
async def create_usuario_template(request: Request):
    print("Usuario get: ", )
    return templates.TemplateResponse("crearUsuario.html.jinja", {"request": request})


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
    elif user.IdRole == 2:
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


#Candidato
@app.post("/candidate/create/", response_model=schemas.CandidateBase)
async def crear_candidato_post(request: Request, 
                        IdCandidato: str = Form(...), 
                        IdFrente: str = Form(...), 
                        IdEleccion: str = Form(...), 
                        IdUsuario: str = Form(...), 
                        Hora: str = Form(...), 
                        Estado: str = Form(...), 
                        db: Session = Depends(get_db)):

    print("Candidato: ", IdCandidato)
    candidate = schemas.FrontCreate(
                              IdCandidato=IdCandidato,          
                              IdFrente=IdFrente,
                              IdEleccion=IdEleccion,
                              IdUsuario=IdUsuario,
                              Hora=Hora,
                              Estado=Estado
                              )
    crudCandidato.create_candidate(db, candidate=candidate)
    candidates = crudCandidato.get_candidates(db)
    for candidate in candidates:
        print('Candidato: ', candidate.IdCandidato)
    return templates.TemplateResponse("listaCandidatoAdministrador.html.jinja", {"request": request , "Candidates": candidates})



@app.get("/candidates/list/", response_class=HTMLResponse, name="listar_candidatos")
async def listar_candidatos(request: Request, db: Session = Depends(get_db)):
    candidates = crudCandidato.get_candidates(db)
    if not candidates:
        print("No candidate found")
    else:
        print(f"Found {len(candidates)} fronts")
        for candidate in candidates:
            print("ID:", candidate.IdCandidato)
            print("Elección:", candidate.IdEleccion)
    return templates.TemplateResponse("listaCandidatoAdministrador.html.jinja", {"request": request, "Candidates": candidates})


@app.post("/candidate/delete/{candidate_id}/", response_class=HTMLResponse)
async def eliminar_candidato(request: Request, candidate_id: int, db: Session = Depends(get_db)):
    crudCandidato.delete_candidate(db=db, candidate_id=candidate_id)
    return RedirectResponse(url='/candidates/list/', status_code=303)


@app.get("/candidate/create/", response_class=HTMLResponse)
async def crear_candidato_template(request: Request, db: Session = Depends(get_db)):
    candidates = crudCandidato.get_candidates(db) 
    return templates.TemplateResponse("crearFrenteAdministrador.html.jinja", {"request": request, "Canidates": candidates})





